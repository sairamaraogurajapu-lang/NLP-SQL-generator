import re

TABLE_COLUMNS = {
    "employees": ["id", "emp_name", "department", "salary", "country", "company"],
    "salaries":  ["id", "emp_id", "emp_name", "base_salary", "bonus", "deductions", "net_salary", "pay_date", "month"],
    "leaves":    ["id", "emp_id", "emp_name", "leave_type", "start_date", "end_date", "days_taken", "status"],
}

TABLE_KEYWORDS = {
    "employees": {"employee", "employees", "staff", "worker", "workers", "people", "person", "member", "members"},
    "salaries":  {"payroll", "payment", "wage", "wages", "net_salary", "base_salary", "compensation", "paid", "bonus", "bonuses", "deduction", "deductions", "net", "base", "salary", "salaries", "record", "records"},
    "leaves":    {"leave", "leaves", "absence", "absences", "vacation", "holiday", "casual", "annual", "maternity", "paternity"},
}

SALARIES_PRIORITY = {"bonus", "bonuses", "deduction", "deductions", "net_salary", "base_salary", "payroll", "wage", "wages", "net", "base"}
LEAVES_PRIORITY   = {"leave", "leaves", "absence", "vacation", "holiday", "casual", "annual", "maternity", "paternity", "sick", "medical", "emergency"}

MONTH_MAP = {
    "january": "January", "february": "February", "march": "March", "april": "April",
    "may": "May", "june": "June", "july": "July", "august": "August",
    "september": "September", "october": "October", "november": "November", "december": "December",
    "jan": "January", "feb": "February", "mar": "March", "apr": "April",
    "jun": "June", "jul": "July", "aug": "August", "sep": "September",
    "oct": "October", "nov": "November", "dec": "December",
}

COLUMN_ALIAS = {
    "employees": {
        "name": "emp_name", "names": "emp_name", "emp_name": "emp_name", "employee": "emp_name",
        "salary": "salary", "salaries": "salary", "pay": "salary", "earn": "salary",
        "earns": "salary", "earning": "salary", "earnings": "salary", "income": "salary",
        "department": "department", "dept": "department", "departments": "department",
        "country": "country", "countries": "country", "location": "country", "locations": "country",
        "company": "company", "companies": "company", "firm": "company",
        "id": "id",
    },
    "salaries": {
        "name": "emp_name", "emp_name": "emp_name", "employee": "emp_name",
        "base": "base_salary", "base_salary": "base_salary", "basic": "base_salary",
        "bonus": "bonus", "bonuses": "bonus",
        "deduction": "deductions", "deductions": "deductions",
        "net": "net_salary", "net_salary": "net_salary",
        "date": "pay_date", "pay_date": "pay_date",
        "month": "month",
        "id": "id", "emp_id": "emp_id",
    },
    "leaves": {
        "name": "emp_name", "emp_name": "emp_name", "employee": "emp_name",
        "type": "leave_type", "leave_type": "leave_type",
        "start": "start_date", "start_date": "start_date",
        "end": "end_date", "end_date": "end_date",
        "days": "days_taken", "days_taken": "days_taken", "duration": "days_taken",
        "status": "status",
        "id": "id", "emp_id": "emp_id",
    },
}

AGGREGATIONS = {
    "count": "COUNT", "total": "SUM", "sum": "SUM",
    "average": "AVG", "avg": "AVG", "mean": "AVG",
    "maximum": "MAX", "max": "MAX",
    "minimum": "MIN", "min": "MIN",
}

WINDOW_PATTERNS = [
    (r"\bassign\s+dense\s*rank\b|\bdense\s*rank\b",  "DENSE_RANK",  "salary", "DESC"),
    (r"\bassign\s+row\s*number\b|\brow\s*number\b",  "ROW_NUMBER",  "salary", "DESC"),
    (r"\bassign\s+rank\b|\brank\b(?!\s*\()",         "RANK",        "salary", "DESC"),
    (r"\blag\b",                                     "LAG",         "salary", "ASC"),
    (r"\blead\b",                                    "LEAD",        "salary", "ASC"),
    (r"\bcumulative\s+sum\b|\brunning\s+total\b",    "SUM",         "salary", "ASC"),
    (r"\bcumulative\s+avg\b|\brunning\s+avg\b",      "AVG",         "salary", "ASC"),
]

COMPARISON_PATTERNS = [
    (r"more than|greater than|higher than|above|over|earn(?:s|ing)? more than|exceed(?:s|ing)?", ">"),
    (r"less than|lower than|below|under|earn(?:s|ing)? less than",                                "<"),
    (r"at least|greater than or equal|no less than|minimum of",                                   ">="),
    (r"at most|less than or equal|no more than|not more than|maximum of",                         "<="),
    (r"equal to|equals|exactly|is exactly",                                                       "="),
    (r"not equal|not equals|different from|other than",                                           "!="),
]

DISTINCT_WORDS  = {"distinct", "unique", "different", "various", "uniquely"}
GROUP_WORDS     = {"group", "grouped", "per", "each"}
ORDER_WORDS     = {"order", "sort", "sorted", "arrange", "arranged"}
LIMIT_WORDS     = {"first", "top", "limit"}
CONDITION_WORDS = {"where", "having", "whose", "which", "that", "belong", "belongs"}
DEPT_KEYWORDS   = {"it", "hr", "finance", "marketing", "sales", "engineering", "operations"}
STATUS_KEYWORDS = {"approved", "pending", "rejected"}
LEAVE_TYPES     = {"sick", "casual", "annual", "maternity", "paternity", "medical", "emergency"}
PARTITION_WORDS = {"within", "per", "each", "across", "inside"}
COMPANY_PATTERN = r"\b(?:working\s+in|working\s+at|works\s+at|works\s+in|at|for|from)\s+([A-Za-z][A-Za-z0-9]+)\b"


def _detect_table(tokens):
    # Month in tokens → salaries
    for token in tokens:
        if token in MONTH_MAP:
            return "salaries"
    # Salaries-specific keywords take priority
    for token in tokens:
        if token in SALARIES_PRIORITY:
            return "salaries"
        if token in LEAVES_PRIORITY:
            return "leaves"
    # salary/record keywords → salaries
    salary_words = {"salary", "salaries", "record", "records"}
    for token in tokens:
        if token in salary_words:
            return "salaries"
    return "employees"


def _detect_aggregation(tokens):
    for token in tokens:
        if token in AGGREGATIONS:
            return AGGREGATIONS[token]
    return None


def _detect_window_function(text_lower, tokens, table):
    alias = COLUMN_ALIAS[table]
    valid = set(TABLE_COLUMNS[table])
    for pattern, func, default_order_col, default_order_dir in WINDOW_PATTERNS:
        if re.search(pattern, text_lower):
            partition_col = None
            for i, token in enumerate(tokens):
                if token in PARTITION_WORDS and i + 1 < len(tokens):
                    col = alias.get(tokens[i + 1], tokens[i + 1])
                    if col in valid:
                        partition_col = col
                        break
            if not partition_col:
                for i, token in enumerate(tokens):
                    if token == "by" and i + 1 < len(tokens):
                        col = alias.get(tokens[i + 1], tokens[i + 1])
                        if col in valid and col != default_order_col:
                            partition_col = col
                            break
            order_col = default_order_col
            order_dir = default_order_dir
            for token in tokens:
                if token in ("desc", "descending"):
                    order_dir = "DESC"
                if token in ("asc", "ascending"):
                    order_dir = "ASC"
            over_parts = []
            if partition_col:
                over_parts.append(f"PARTITION BY {partition_col}")
            over_parts.append(f"ORDER BY {order_col} {order_dir}")
            over_clause = " ".join(over_parts)
            if func in ("LAG", "LEAD"):
                window_expr = f"{func}({order_col}) OVER ({over_clause}) AS {func.lower()}_{order_col}"
            elif func in ("SUM", "AVG"):
                window_expr = f"{func}({order_col}) OVER ({over_clause}) AS running_{func.lower()}"
            else:
                window_expr = f"{func}() OVER ({over_clause}) AS salary_rank"
            select_cols = ["id", "emp_name"]
            if partition_col and partition_col not in select_cols:
                select_cols.append(partition_col)
            if order_col not in select_cols:
                select_cols.append(order_col)
            cols_str = ",\n    ".join(select_cols)
            return f"SELECT\n    {cols_str},\n    {window_expr}"
    return None


def _detect_columns(tokens, table):
    alias = COLUMN_ALIAS[table]
    valid = set(TABLE_COLUMNS[table])
    seen, cols = set(), []
    for t in tokens:
        if t in alias:
            col = alias[t]
            if col not in seen and col in valid:
                seen.add(col)
                cols.append(col)
    return cols


def _detect_group(tokens, table):
    alias = COLUMN_ALIAS[table]
    valid = set(TABLE_COLUMNS[table])
    for i, token in enumerate(tokens):
        if token in GROUP_WORDS and i + 1 < len(tokens):
            col = alias.get(tokens[i + 1], tokens[i + 1])
            if col in valid:
                return col
    for i, token in enumerate(tokens):
        if token == "by" and i + 1 < len(tokens):
            if i > 0 and tokens[i - 1] in ORDER_WORDS:
                continue
            col = alias.get(tokens[i + 1], tokens[i + 1])
            if col in valid:
                return col
    return None


def _detect_order(tokens, table):
    alias = COLUMN_ALIAS[table]
    valid = set(TABLE_COLUMNS[table])
    order_col, order_dir = None, "ASC"
    for i, token in enumerate(tokens):
        if token in ORDER_WORDS and i + 1 < len(tokens):
            next_tok = tokens[i + 1]
            if next_tok == "by" and i + 2 < len(tokens):
                next_tok = tokens[i + 2]
            col = alias.get(next_tok, next_tok)
            if col in valid:
                order_col = col
        if token in ("desc", "descending"):
            order_dir = "DESC"
        if token in ("asc", "ascending"):
            order_dir = "ASC"
    return order_col, order_dir


def _detect_limit(tokens):
    for i, token in enumerate(tokens):
        if token in LIMIT_WORDS:
            for j in range(i + 1, min(i + 3, len(tokens))):
                if tokens[j].isdigit():
                    return tokens[j]
            return "1"
    return None


def _detect_where(text_lower, tokens, table, original_text):
    conditions = []

    # 0. BETWEEN
    between_match = re.search(r"between\s+([\d,]+)\s+and\s+([\d,]+)", text_lower)
    if between_match:
        val1 = between_match.group(1).replace(",", "")
        val2 = between_match.group(2).replace(",", "")
        col  = "base_salary" if table == "salaries" else "salary"
        if any(w in text_lower for w in ["days", "duration"]):
            col = "days_taken"
        return f"WHERE {col} >= {val1} AND {col} < {val2}"

    # 0b. Direct symbol comparison
    symbol_match = re.search(r"salary\s*(>=|<=|!=|>|<|=)\s*([\d,]+)", text_lower)
    if symbol_match:
        operator = symbol_match.group(1)
        number   = symbol_match.group(2).replace(",", "")
        col      = "base_salary" if table == "salaries" else "salary"
        conditions.append(f"{col} {operator} {number}")

    # 1. Month filter — highest priority for salaries
    if table == "salaries":
        for token in tokens:
            if token in MONTH_MAP:
                conditions.append(f"month = '{MONTH_MAP[token]}'")
                break

    # 2. Numeric comparison
    if not any(c for c in conditions if any(op in c for op in [">", "<", "="])):
        for pattern, operator in COMPARISON_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                after     = text_lower[match.end():]
                num_match = re.search(r"[\d,]+", after)
                if num_match:
                    number = num_match.group().replace(",", "")
                    if any(w in text_lower for w in ["days", "duration"]):
                        col = "days_taken"
                    elif any(w in text_lower for w in ["bonus", "bonuses"]):
                        col = "bonus"
                    elif any(w in text_lower for w in ["net salary", "net_salary", "net"]):
                        col = "net_salary"
                    elif any(w in text_lower for w in ["base salary", "base_salary", "basic"]):
                        col = "base_salary"
                    elif any(w in text_lower for w in ["deduction", "deductions"]):
                        col = "deductions"
                    else:
                        col = "base_salary" if table == "salaries" else "salary"
                    conditions.append(f"{col} {operator} {number}")
                    break

    # 3. Department filter
    for dept in DEPT_KEYWORDS:
        if dept in tokens:
            conditions.append(f"LOWER(department) = '{dept.lower()}'")
            break

    # 4. Company filter
    company_match = re.search(COMPANY_PATTERN, text_lower)
    if company_match:
        company_lower = company_match.group(1)
        is_month      = company_lower in MONTH_MAP
        is_country    = company_lower in {"usa", "uk", "uae", "india", "germany", "france", "canada", "australia"}
        orig          = re.search(COMPANY_PATTERN, original_text, re.IGNORECASE)
        orig_word     = orig.group(1) if orig else company_lower
        is_country    = is_country or orig_word.isupper()
        if company_lower not in DEPT_KEYWORDS and company_lower not in {"the", "a", "an"} and table == "employees" and not is_country and not is_month:
            conditions.append(f"company = '{orig_word}'")

    # 5. Country filter
    if not company_match or table != "employees":
        country_match = re.search(r"\b(?:from|in)\s+([A-Za-z]+)\b", text_lower)
        if country_match:
            country_lower = country_match.group(1)
            orig_c        = re.search(r"\b(?:from|in)\s+([A-Za-z]+)\b", original_text, re.IGNORECASE)
            country_orig  = orig_c.group(1) if orig_c else country_lower
            is_country    = country_orig.isupper() or country_lower in {"usa", "uk", "uae", "india", "germany", "france", "canada", "australia"}
            if country_lower not in DEPT_KEYWORDS and country_lower not in MONTH_MAP and table == "employees":
                conditions.append(f"country = '{country_orig}'")

    # 6. Leave status filter
    for status in STATUS_KEYWORDS:
        if status in tokens:
            conditions.append(f"status = '{status.capitalize()}'")
            break

    # 7. Leave type filter
    for ltype in LEAVE_TYPES:
        if ltype in tokens:
            conditions.append(f"leave_type = '{ltype.capitalize()}'")
            break

    # 8. Person name detection
    if not conditions:
        name_match = re.search(r"\b(?:of|for|named?|called)\s+([A-Z][a-z]+)\b", original_text)
        if name_match:
            name = name_match.group(1)
            if name not in MONTH_MAP.values():
                conditions.append(f"emp_name = '{name}'")

    # 9. Generic condition
    if not conditions:
        alias = COLUMN_ALIAS[table]
        valid = set(TABLE_COLUMNS[table])
        for i, token in enumerate(tokens):
            if token in CONDITION_WORDS and i + 2 < len(tokens):
                col = alias.get(tokens[i + 1], tokens[i + 1])
                val = tokens[i + 2].rstrip(".,;")
                if col not in valid:
                    continue
                conditions.append(f"{col} = {val}" if val.isdigit() else f"{col} = '{val}'")
                break

    if conditions:
        return "WHERE " + " AND ".join(conditions)
    return None


def _detect_insert(original_text, text_lower, tokens):
    insert_triggers = {"add", "insert", "create", "put", "new", "give", "assign", "grant"}

    if not any(w in tokens for w in insert_triggers):
        return None

    sal_triggers   = {"salary", "salaries", "payroll"}
    leave_triggers = {"leave", "leaves"}

    if any(w in tokens for w in sal_triggers):
        target_table = "salaries"
    elif any(w in tokens for w in leave_triggers):
        target_table = "leaves"
    else:
        target_table = "employees"

    # --- Leave insertion: give leave to Ram sick 2 days ---
    if target_table == "leaves":
        name_match = re.search(r"\b(?:to|for|give|assign|grant)\s+([A-Z][a-z]+)", original_text)
        emp_name   = name_match.group(1) if name_match else None
        leave_type = None
        for lt in LEAVE_TYPES:
            if lt in tokens:
                leave_type = lt.capitalize()
                break
        days_match = re.search(r"(\d+)\s*(?:days?|day)", text_lower)
        days = days_match.group(1) if days_match else None
        columns, values = [], []
        if emp_name:
            columns.append("emp_name"); values.append(f"'{emp_name}'")
        if leave_type:
            columns.append("leave_type"); values.append(f"'{leave_type}'")
        if days:
            columns.append("days_taken"); values.append(days)
        if columns:
            return f"INSERT INTO leaves ({', '.join(columns)})\nVALUES ({', '.join(values)});"
        return None

    # --- Format 1: key:value or key-:value pairs ---
    pairs = re.findall(r"([a-zA-Z][a-zA-Z0-9_ ]*)\s*-?\s*:\s*([^,\n]+)", original_text)
    skip  = {"add", "insert", "create", "new", "put", "give", "assign", "grant", "data",
             "record", "in", "into", "table", "that", "the", "a", "an", "employee", "employees"}
    if pairs:
        columns, values = [], []
        for col_raw, val_raw in pairs:
            col = col_raw.strip().lower().replace(" ", "_")
            val = val_raw.strip().rstrip(",").strip()
            if col in skip or len(col) < 2:
                continue
            columns.append(col)
            values.append(val if re.match(r"^\d+(\.\d+)?$", val) else f"'{val.title()}'")
        if columns:
            return f"INSERT INTO {target_table} ({', '.join(columns)})\nVALUES ({', '.join(values)});"

    # --- Format 2: positional --- add new employee <name> <dept> <salary> <country> ---
    if target_table == "employees":
        stop_words = {"add", "new", "insert", "create", "put", "give", "assign", "grant",
                      "employee", "employees", "emp", "staff", "worker", "member",
                      "a", "an", "the", "into", "in", "table"}
        values_raw = [t for t in tokens if t not in stop_words]
        dept_keywords    = {"it", "hr", "finance", "marketing", "sales", "engineering", "operations"}
        country_keywords = {"india", "usa", "uk", "germany", "france", "canada", "australia", "uae"}
        company_keywords = {"techcorp", "peopleinc", "fingroup", "datasoft"}
        name_parts, dept, salary, country, company = [], None, None, None, None
        for val in values_raw:
            if val in dept_keywords and not dept:
                dept = val.upper()
            elif val in country_keywords and not country:
                country = val.title()
            elif val in company_keywords and not company:
                company = val.title()
            elif re.match(r"^\d+$", val) and not salary:
                salary = val
            elif not dept and not salary:
                name_parts.append(val.title())
        columns, values = [], []
        if name_parts:
            columns.append("emp_name"); values.append(f"'{' '.join(name_parts)}'")
        if dept:
            columns.append("department"); values.append(f"'{dept}'")
        if salary:
            columns.append("salary"); values.append(salary)
        if country:
            columns.append("country"); values.append(f"'{country}'")
        if company:
            columns.append("company"); values.append(f"'{company}'")
        if columns:
            return f"INSERT INTO {target_table} ({', '.join(columns)})\nVALUES ({', '.join(values)});"

    return None


def _detect_delete(original_text, text_lower, tokens):
    delete_triggers = {"remove", "delete", "erase", "drop", "eliminate", "purge"}

    if not any(w in tokens for w in delete_triggers):
        return None

    # detect table
    if any(w in tokens for w in {"leave", "leaves"}):
        target_table = "leaves"
    elif any(w in tokens for w in {"salary", "salaries", "payroll"}):
        target_table = "salaries"
    else:
        target_table = "employees"

    conditions = []

    # detect name: remove employee named Krishna / remove Krishna from database
    name_match = re.search(
        r"\b(?:named?|called|employee|emp|with\s+name|name\s+is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
        original_text
    )
    if not name_match:
        # fallback: remove <Name> from ...
        name_match = re.search(
            r"\b(?:remove|delete|erase|eliminate)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b",
            original_text
        )
    if name_match:
        name = name_match.group(1).strip()
        conditions.append(f"emp_name = '{name}'")

    # detect department filter
    for dept in DEPT_KEYWORDS:
        if dept in tokens:
            conditions.append(f"LOWER(department) = '{dept.lower()}'")
            break

    # detect leave type filter
    for ltype in LEAVE_TYPES:
        if ltype in tokens:
            conditions.append(f"leave_type = '{ltype.capitalize()}'")
            break

    # detect id filter
    id_match = re.search(r"\bid\s*[=:]?\s*(\d+)\b", text_lower)
    if id_match:
        conditions.append(f"id = {id_match.group(1)}")

    if not conditions:
        return None

    where = "WHERE " + " AND ".join(conditions)
    return f"DELETE FROM {target_table}\n{where};"


def _detect_update(original_text, text_lower, tokens):
    update_triggers = {"update", "change", "modify", "edit", "correct", "set"}
    salary_triggers = {"bonus", "net", "base", "deduction", "pay"}

    has_update = any(w in tokens for w in update_triggers)
    has_add_sal = "add" in tokens and any(w in tokens for w in salary_triggers)

    if not (has_update or has_add_sal):
        return None

    # detect table — salary alone stays in employees, bonus/net/base go to salaries
    if any(w in tokens for w in {"leave", "leaves"}):
        target_table = "leaves"
    elif any(w in tokens for w in {"bonus", "net_salary", "base_salary", "deduction", "payroll"}):
        target_table = "salaries"
    else:
        target_table = "employees"

    # detect employee name from original text
    emp_name = None

    # Pattern 1: Update <Name> department/salary/country/company/bonus
    m = re.search(
        r"\b(?:update|change|modify|edit)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+(?:department|salary|country|company|bonus|dept)",
        original_text, re.IGNORECASE
    )
    if m:
        emp_name = m.group(1).strip().title()

    # Pattern 2: of/for/named <Name>
    if not emp_name:
        m = re.search(
            r"\b(?:of|for|named?|called)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)",
            original_text, re.IGNORECASE
        )
        if m:
            emp_name = m.group(1).strip().title()

    # column map per table
    col_map = {
        "employees": {
            "salary": "salary", "pay": "salary", "department": "department",
            "dept": "department", "country": "country", "company": "company",
        },
        "salaries": {
            "salary": "net_salary", "net": "net_salary", "net_salary": "net_salary",
            "base": "base_salary", "base_salary": "base_salary",
            "bonus": "bonus", "bonuses": "bonus",
            "deduction": "deductions", "deductions": "deductions",
        },
        "leaves": {
            "status": "status", "leave_type": "leave_type", "days": "days_taken",
        },
    }

    active_map = col_map[target_table]
    set_clauses = []

    # pattern: col <number> e.g. salary 90000
    for i, token in enumerate(tokens):
        if token in active_map and i + 1 < len(tokens):
            val = tokens[i + 1]
            if re.match(r"^\d+(\.\d+)?$", val):
                clause = f"    {active_map[token]} = {val}"
                if clause not in set_clauses:
                    set_clauses.append(clause)

    # pattern: col to <value> e.g. salary to 90000 or department to HR
    to_match = re.search(r"(salary|bonus|department|dept|country|company)\s+to\s+([\w]+)", text_lower)
    if to_match:
        col_raw = to_match.group(1).strip()
        col     = active_map.get(col_raw, col_raw)
        val     = to_match.group(2).strip()
        if re.match(r"^\d+(\.\d+)?$", val):
            clause = f"    {col} = {val}"
        elif col_raw in {"dept", "department"}:
            formatted = val.upper()
            clause = f"    {col} = '{formatted}'"
        else:
            formatted = val.title()
            clause = f"    {col} = '{formatted}'"
        if clause not in set_clauses:
            set_clauses.append(clause)

    if not set_clauses:
        return None

    set_str = ",\n".join(set_clauses)
    where   = f"WHERE emp_name = '{emp_name}'" if emp_name else "WHERE emp_name = ''"
    return f"UPDATE {target_table}\nSET\n{set_str}\n{where};"


def _detect_alter(text_lower, tokens, original_text):
    # Don't trigger ALTER if this looks like an INSERT (has numeric salary values)
    if re.search(r"\b\d{4,}\b", text_lower):
        return None
    if any(w in tokens for w in {"employee", "employees", "emp", "staff", "worker", "member", "new"}):
        return None

    # Must explicitly mention 'column' or 'field' to trigger ALTER
    if not any(w in tokens for w in {"column", "field", "rename", "modify", "alter", "drop", "type"}):
        return None

    table_map = {
        "employee": "employees", "employees": "employees",
        "salaries": "salaries", "salary": "salaries",
        "leaves": "leaves", "leave": "leaves",
    }
    target_table = "employees"
    for token in tokens:
        if token in table_map:
            target_table = table_map[token]
            break

    # Valid column names only — prevent junk columns
    valid_col_names = {
        "email", "phone", "phone_number", "mobile", "address", "age",
        "dob", "birthdate", "joining_date", "gender", "city",
        "description", "notes", "code", "status"
    }

    type_map = {
        "email": "VARCHAR(255)",
        "phone": "VARCHAR(15)", "phone_number": "VARCHAR(15)", "mobile": "VARCHAR(15)",
        "address": "TEXT", "age": "INT",
        "dob": "DATE", "birthdate": "DATE", "joining_date": "DATE",
        "gender": "VARCHAR(10)", "city": "VARCHAR(100)",
        "description": "TEXT", "notes": "TEXT",
        "code": "VARCHAR(20)", "status": "VARCHAR(50)",
    }

    # ADD COLUMN
    if any(w in tokens for w in ["add", "adding", "include"]):
        col_match = re.search(
            r"\b(?:add|adding|include)\s+(?:a\s+)?(?:column\s+)?([a-z_]+(?:\s+[a-z_]+)?)\s*(?:column|field|to|in)?",
            text_lower
        )
        if col_match:
            col_raw  = col_match.group(1).strip().replace(" ", "_")
            if col_raw not in valid_col_names:
                return None
            col_type = type_map.get(col_raw, "VARCHAR(255)")
            return f"ALTER TABLE {target_table}\nADD COLUMN {col_raw} {col_type};"

    # DROP COLUMN
    if any(w in tokens for w in ["drop", "remove", "delete", "removing"]):
        col_match = re.search(
            r"\b(?:drop|remove|delete|removing)\s+(?:column\s+)([a-z_]+)",
            text_lower
        )
        if col_match:
            col_name = col_match.group(1)
            return f"ALTER TABLE {target_table}\nDROP COLUMN {col_name};"

    # RENAME COLUMN
    if "rename" in tokens:
        rename_match = re.search(r"rename\s+(?:column\s+)?([a-z_]+)\s+to\s+([a-z_]+)", text_lower)
        if rename_match:
            old_col = rename_match.group(1)
            new_col = rename_match.group(2)
            return f"ALTER TABLE {target_table}\nRENAME COLUMN {old_col} TO {new_col};"

    return None


def _detect_join(text_lower, tokens):
    emp_cols   = {"department", "dept", "country", "location", "company"}
    sal_cols   = {"net_salary", "base_salary", "bonus", "deductions", "net", "base", "payroll", "salary", "salaries"}
    leave_cols = {"leave_type", "days_taken", "start_date", "end_date", "leave", "leaves", "leave_status"}

    has_emp   = any(t in emp_cols   for t in tokens) or "employee" in tokens or "employees" in tokens
    has_sal   = any(t in sal_cols   for t in tokens)
    has_leave = any(t in leave_cols for t in tokens) or "on leave" in text_lower

    # 3-table JOIN: employees + salaries + leaves
    if has_sal and has_leave:
        select_cols = ["e.emp_name", "s.net_salary"]
        if any(t in {"department", "dept"} for t in tokens):
            select_cols.append("e.department")
        if any(t in {"leave_type", "leave"} for t in tokens):
            select_cols.append("l.leave_type")
        if any(t in {"status"} for t in tokens):
            select_cols.append("l.status")
        if any(t in {"days", "days_taken"} for t in tokens):
            select_cols.append("l.days_taken")

        # detect leave type filter
        leave_filter = ""
        all_leave_types = {"sick", "casual", "annual", "maternity", "paternity", "medical", "emergency"}
        for token in tokens:
            if token in all_leave_types:
                if "l.leave_type" not in select_cols:
                    select_cols.append("l.leave_type")
                leave_filter = f"\nWHERE l.leave_type = '{token.capitalize()}'"
                break

        return (
            f"SELECT {', '.join(select_cols)}\n"
            f"FROM employees e\n"
            f"JOIN salaries s ON e.id = s.emp_id\n"
            f"JOIN leaves l ON e.id = l.emp_id"
            f"{leave_filter};"
        )

    # employees + salaries JOIN
    if has_emp and has_sal:
        select_cols = ["e.emp_name", "e.department", "s.net_salary"]
        if any(t in {"bonus", "bonuses"} for t in tokens):
            select_cols.append("s.bonus")
        if any(t in {"country", "location"} for t in tokens):
            select_cols.append("e.country")
        if any(t in {"company"} for t in tokens):
            select_cols.append("e.company")
        if any(t in {"base", "base_salary"} for t in tokens):
            select_cols.append("s.base_salary")
        return f"SELECT {', '.join(select_cols)}\nFROM employees e\nJOIN salaries s ON e.emp_name = s.emp_name;"

    # employees + leaves JOIN
    if has_emp and has_leave:
        select_cols = ["e.emp_name", "e.department", "l.leave_type", "l.status"]
        if any(t in {"days", "days_taken", "duration", "total"} for t in tokens):
            return (
                f"SELECT e.emp_name, SUM(l.days_taken) AS total_leaves_taken\n"
                f"FROM employees e\n"
                f"LEFT JOIN leaves l ON e.emp_name = l.emp_name\n"
                f"GROUP BY e.emp_name\n"
                f"ORDER BY total_leaves_taken DESC;"
            )
        if any(t in {"start", "start_date"} for t in tokens):
            select_cols.append("l.start_date")
        if any(t in {"end", "end_date"} for t in tokens):
            select_cols.append("l.end_date")
        return f"SELECT {', '.join(select_cols)}\nFROM employees e\nLEFT JOIN leaves l ON e.emp_name = l.emp_name;"

    return None


def _build_select(agg_func, use_distinct, columns, where_clause, group_col, table="employees"):
    if agg_func and group_col:
        # choose correct column for aggregation based on table
        if agg_func == "COUNT":
            return f"SELECT {group_col}, COUNT(*) AS {group_col}_count"
        elif agg_func == "SUM" and table == "leaves":
            return f"SELECT {group_col}, SUM(days_taken) AS total_days"
        elif agg_func == "SUM" and table == "salaries":
            return f"SELECT {group_col}, SUM(net_salary) AS total_salary"
        elif agg_func == "AVG" and table == "leaves":
            return f"SELECT {group_col}, AVG(days_taken) AS avg_days"
        elif agg_func == "AVG" and table == "salaries":
            return f"SELECT {group_col}, AVG(net_salary) AS avg_salary"
        elif agg_func == "MAX":
            col = "days_taken" if table == "leaves" else "net_salary" if table == "salaries" else "salary"
            return f"SELECT {group_col}, MAX({col}) AS max_{col}"
        elif agg_func == "MIN":
            col = "days_taken" if table == "leaves" else "net_salary" if table == "salaries" else "salary"
            return f"SELECT {group_col}, MIN({col}) AS min_{col}"
        else:
            return f"SELECT {group_col}, COUNT(*) AS {group_col}_count"
    if agg_func:
        col   = columns[0] if columns else "*"
        alias = f"{agg_func.lower()}_{col}" if col != "*" else "total_count"
        return f"SELECT {agg_func}({col}) AS {alias}"
    if use_distinct and columns:
        return f"SELECT DISTINCT {columns[0]}"
    if where_clause and columns:
        columns = [c for c in columns if c != "emp_name"]
        if not columns:
            return "SELECT *"
        return f"SELECT emp_name, {', '.join(columns)}"
    if where_clause and not columns:
        return "SELECT *"
    if columns:
        return f"SELECT {', '.join(columns)}"
    return "SELECT *"


def get_sql(text):
    original_text = text.strip()
    text_lower    = re.sub(r"[^\w\s><!=]", " ", original_text.lower())
    tokens        = text_lower.split()

    table = _detect_table(tokens)

    window_select = _detect_window_function(text_lower, tokens, table)
    if window_select:
        return f"{window_select}\nFROM {table};"

    # DELETE detection
    delete_result = _detect_delete(original_text, text_lower, tokens)
    if delete_result:
        return delete_result

    # INSERT detection — highest priority when 'add/insert' + employee data present
    insert_result = _detect_insert(original_text, text_lower, tokens)
    if insert_result:
        return insert_result

    # UPDATE detection
    update_result = _detect_update(original_text, text_lower, tokens)
    if update_result:
        return update_result

    # ALTER TABLE detection
    alter_result = _detect_alter(text_lower, tokens, original_text)
    if alter_result:
        return alter_result

    # highest/lowest salary per department — must be before JOIN detection
    if any(w in tokens for w in ["highest", "maximum", "most", "lowest", "minimum", "least"]):
        if any(w in tokens for w in ["salary", "salaries", "pay"]) and any(w in tokens for w in ["department", "dept", "per", "each"]):
            if any(w in tokens for w in ["highest", "maximum", "most"]):
                return (
                    "SELECT department, MAX(salary) AS highest_salary\n"
                    "FROM employees\n"
                    "GROUP BY department\n"
                    "ORDER BY highest_salary DESC;"
                )
            else:
                return (
                    "SELECT department, MIN(salary) AS lowest_salary\n"
                    "FROM employees\n"
                    "GROUP BY department\n"
                    "ORDER BY lowest_salary ASC;"
                )

    # total salary by company
    if any(w in tokens for w in ["total", "sum"]) and any(w in tokens for w in ["salary", "salaries", "pay"]) and any(w in tokens for w in ["company", "companies", "firm"]):
        return (
            "SELECT e.company, SUM(s.net_salary) AS total_salary\n"
            "FROM employees e\n"
            "JOIN salaries s ON e.emp_name = s.emp_name\n"
            "GROUP BY e.company\n"
            "ORDER BY total_salary DESC;"
        )

    # JOIN detection: when query mentions columns from multiple tables
    join_result = _detect_join(text_lower, tokens)
    if join_result:
        return join_result

    # average salary per department
    if "average" in tokens and any(w in tokens for w in ["salary", "salaries", "pay", "income"]):
        if any(w in tokens for w in ["department", "dept", "per", "each", "by"]):
            return (
                "SELECT department, ROUND(AVG(salary), 2) AS average_salary\n"
                "FROM employees\n"
                "GROUP BY department\n"
                "ORDER BY average_salary DESC;"
            )
        return "SELECT ROUND(AVG(salary), 2) AS average_salary\nFROM employees;"

    alias = COLUMN_ALIAS[table]
    valid = set(TABLE_COLUMNS[table])
    for i, token in enumerate(tokens):
        if token in ("highest", "maximum", "most") and i + 1 < len(tokens):
            col = alias.get(tokens[i + 1], tokens[i + 1])
            # highest salary per/each/by department
            if col in valid and any(w in tokens for w in ["department", "dept", "per", "each"]):
                return (
                    f"SELECT department, MAX(salary) AS highest_salary\n"
                    f"FROM employees\n"
                    f"GROUP BY department\n"
                    f"ORDER BY highest_salary DESC;"
                )
            if col in valid:
                return f"SELECT *\nFROM {table}\nORDER BY {col} DESC\nLIMIT 1;"
        if token in ("lowest", "minimum", "least") and i + 1 < len(tokens):
            col = alias.get(tokens[i + 1], tokens[i + 1])
            if col in valid and any(w in tokens for w in ["department", "dept", "per", "each"]):
                return (
                    f"SELECT department, MIN(salary) AS lowest_salary\n"
                    f"FROM employees\n"
                    f"GROUP BY department\n"
                    f"ORDER BY lowest_salary DESC;"
                )
            if col in valid:
                return f"SELECT *\nFROM {table}\nORDER BY {col} ASC\nLIMIT 1;"

    agg_func     = _detect_aggregation(tokens)
    use_distinct = any(w in tokens for w in DISTINCT_WORDS)
    columns      = _detect_columns(tokens, table)
    where_clause = _detect_where(text_lower, tokens, table, original_text)
    group_col    = None if use_distinct else _detect_group(tokens, table)
    order_col, order_dir = (None, "ASC") if use_distinct else _detect_order(tokens, table)
    limit        = _detect_limit(tokens)

    select = _build_select(agg_func, use_distinct, columns, where_clause, group_col, table)

    query = f"{select}\nFROM {table}"
    if where_clause:
        query += f"\n{where_clause}"
    if group_col:
        query += f"\nGROUP BY {group_col}"
    if order_col:
        query += f"\nORDER BY {order_col} {order_dir}"
    if limit:
        query += f"\nLIMIT {limit}"

    return query + ";"
