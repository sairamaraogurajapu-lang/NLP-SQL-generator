export const getSQL = (text) => {
  text = text.toLowerCase();

  if (text.includes("all")) return "SELECT *";
  if (text.includes("count")) return "COUNT";
  if (text.includes("first")) return "LIMIT 1";

  return "UNKNOWN";
};