function isSeasonValid(lastAuthDateString, now = new Date()) {
    const month = now.getUTCMonth();
    const year = now.getUTCFullYear();
  
    let seasonStart;
    if (month >= 8 && month <= 10) {
        // Осень: сентябрь — ноябрь
        console.log("Осень");
      seasonStart = new Date(Date.UTC(year, 8, 1)); // 1 сентября
    } else if (month >= 11 || month === 0 || month === 1) {
        console.log("Зима");
      seasonStart = new Date(Date.UTC(month === 11 ? year : year - 1, 11, 1)); // 1 декабря
    } else if (month >= 2 && month <= 4) {
        console.log("Весна");
      seasonStart = new Date(Date.UTC(year, 2, 1)); // 1 марта
    } else {
        console.log("Лето");
      seasonStart = new Date(Date.UTC(year, 5, 1)); // 1 июня
    }
  
    if (!lastAuthDateString) return false;
  
    const savedTime = new Date(lastAuthDateString);
    console.log("Сравнение:", savedTime.toISOString(), ">=", seasonStart.toISOString(), "==", savedTime >= seasonStart);
    return savedTime >= seasonStart;
  }


// Старт Лета
console.log("1 Старт лета - false", isSeasonValid("2025-05-30T08:00:00Z", new Date("2025-06-01T10:00:00Z"))); // false

// Летом в сезоне
console.log("2 Летом в сезоне - true", isSeasonValid("2025-06-30T08:00:00Z", new Date("2025-07-01T10:00:00Z"))); // false// Старт Лета
console.log("3 Летом в сезоне - true", isSeasonValid("2025-07-30T08:00:00Z", new Date("2025-08-05T10:00:00Z"))); // false// Старт Лета
console.log("4 Летом в сезоне - true", isSeasonValid("2025-08-18T08:00:00Z", new Date("2025-08-18T10:00:00Z"))); // false

// Тест: старт весны
console.log("5 Старт весны - false", isSeasonValid("2025-02-28T08:00:00Z", new Date("2025-03-01T10:00:00Z"))); // false
// Весной в сезоне
console.log("6 Весной в сезоне - true", isSeasonValid("2025-03-01T08:00:00Z", new Date("2025-03-01T10:00:00Z"))); // false// Старт Лета
console.log("7 Весной в сезоне - true", isSeasonValid("2025-04-18T08:00:00Z", new Date("2025-04-19T10:00:00Z"))); // false// Старт Лета
console.log("8 Весной в сезоне - true", isSeasonValid("2025-03-01T08:00:00Z", new Date("2025-05-30T10:00:00Z"))); // false

// Тест: старт зимы
console.log("9 Старт зимы - false",isSeasonValid("2025-10-02T08:00:00Z", new Date("2025-12-01T10:00:00Z"))); // true
// Зимой в сезоне
console.log("10 Зимой в сезоне - true", isSeasonValid("2025-12-01T08:00:00Z", new Date("2025-12-01T10:00:00Z"))); // false// Старт Лета
console.log("11 Зимой в сезоне - true", isSeasonValid("2026-01-18T08:00:00Z", new Date("2026-02-01T10:00:00Z"))); // false// Старт Лета
console.log("12 Зимой в сезоне - true", isSeasonValid("2025-12-18T08:00:00Z", new Date("2026-02-28T10:00:00Z"))); // false

// Тест: старт осени
console.log("13 Старт осени - false",isSeasonValid("2024-08-31T08:00:00Z", new Date("2025-09-01T10:00:00Z"))); // true
// Осенью в сезоне
console.log("14 сенью в сезоне - true", isSeasonValid("2025-09-01T08:00:00Z", new Date("2025-09-01T10:00:00Z"))); // false// Старт Лета
console.log("15 сенью в сезоне - фолс", isSeasonValid("2024-09-01T08:00:00Z", new Date("2025-09-02T10:00:00Z"))); // false// Старт Лета
console.log("16 сенью в сезоне - true", isSeasonValid("2025-10-04T08:00:00Z", new Date("2025-11-05T10:00:00Z"))); // false

// Тест: проверка следующего года
console.log("17 Следующий год в сезоне - true",isSeasonValid("2025-12-15T08:00:00Z", new Date("2026-01-01T10:00:00Z"))); // false
// Тест: проверка следующего года
console.log("18 Следующий год НЕ в сезоне - false",isSeasonValid("2025-11-15T08:00:00Z", new Date("2026-01-02T10:00:00Z"))); // false

//Успешная авторизация ровно в начале сезона
console.log("19 Старт весны - true", isSeasonValid("2025-03-01T00:00:00Z", new Date("2025-03-01T00:00:01Z"))); // true

console.log("20 Сезон начался час назад", isSeasonValid("2025-06-01T00:59:59Z", new Date("2025-06-01T01:00:00Z"))); // false

console.log("21 Повторная авторизация в том же сезоне - true", isSeasonValid("2025-09-15T08:00:00Z", new Date("2025-10-01T10:00:00Z"))); // true

console.log("23 Нет даты авторизации - false", isSeasonValid(null, new Date("2025-06-01T10:00:00Z"))); // false
console.log("24 Невалидная строка - false", isSeasonValid("not-a-date", new Date("2025-06-01T10:00:00Z"))); // false
console.log("26 Декабрь → Январь - true", isSeasonValid("2025-12-01T00:00:00Z", new Date("2026-01-15T10:00:00Z"))); // true
