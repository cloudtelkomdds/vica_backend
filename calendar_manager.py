from datetime import datetime

class CalendarManager:
    @staticmethod
    def __get_month_name(number):
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
        return months[number]

    @staticmethod
    def __add_padding_to_number(number):
        if len(number) < 2:
            return "0{0}".format(number)
        return number

    @staticmethod
    def __format_date(day, month, year, hour, minute, second):
        day_str = CalendarManager.__add_padding_to_number(str(day))
        month_str = CalendarManager.__get_month_name(str(month))
        year_str = str(year)
        hour_str = CalendarManager.__add_padding_to_number(str(hour))
        minute_str = CalendarManager.__add_padding_to_number(str(minute))
        second_str = CalendarManager.__add_padding_to_number(str(second))

        date_format = "{0} {1} {2} {3}.{4}.{5}"
        return date_format.format(day_str, month_str, year_str, hour_str, minute_str, second_str)

    @staticmethod
    def get_now_date():
        now = datetime.now()
        return CalendarManager.__format_date(day=now.day,
                                             month=now.month,
                                             year=now.year,
                                             hour=now.hour,
                                             minute=now.minute,
                                             second=now.second)

if __name__ == "__main__":
    print(CalendarManager.get_now_date())