const lowerCased = [
    "for",
    "and",
    "nor",
    "but",
    "or",
    "yet",
    "so",
    "at",
    "by",
    "in",
    "as",
    "if",
    "of",
  ];
  
  export function titleCase(str) {
    str = str.toLowerCase().split(" ");
    for (var i = 0; i < str.length; i++) {
      if (i !== 0 && i !== str.length - 1 && lowerCased.includes(str[i])) {
        str[i] = str[i].toLowerCase();
      } else {
        str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
      }
    }
    return str.join(" ");
  }
  