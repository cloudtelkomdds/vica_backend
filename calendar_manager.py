from datetime import datetime

class CalendarManager:
    months = {
        "1": "January",
        "2": "February",
        "3": "March",
        "4": "April",
        "5": "May",
        "6": "June",
        "7": "July",
        "8": "August",
        "9": "September",
        "10": "October",
        "11": "November",
        "12": "December",
    }

    @staticmethod
    def get_now_date():
        now = datetime.now()
        year = str(now.year)
        month = str(now.month)
        month = CalendarManager.months[month]
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        date_format = "{0} {1} {2} {3}.{4}.{5}".format(day, month, year, hour, minute, second)
        return date_format

if __name__ == "__main__":
    print(CalendarManager.get_now_date())