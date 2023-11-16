import datetime
import pytz

# Define a constant variable for the Argentina time zone (GMT-3)
ARGENTINA_TZ = pytz.timezone("America/Argentina/Buenos_Aires")

# Define a function that takes a string with a GMT date and time in ISO 8601 format
def convert_gmt_to_argentina(gmt):
  gmt = gmt.replace('Z', '+00:00')
  # Create a datetime object from the string, assuming it is in the UTC time zone
  utc_dt = datetime.datetime.fromisoformat(gmt).replace(tzinfo=pytz.utc)
  # Create a datetime object with the Argentina time zone
  
  arg_dt = utc_dt.astimezone(ARGENTINA_TZ)
  # Return the datetime object with the Argentina time zone
  return arg_dt

# Example of using the function
gmt = "2023-11-08T13:51:06.000Z" # Date and time GMT given by the user

arg = convert_gmt_to_argentina(gmt) # Date and time in Argentina
print(f"The date and time {gmt} in GMT corresponds to {arg} in Argentina.") # Print the result


def eliminate_lf_cr(input_string):
    # Replace LF and CR characters with an empty string
    result_string = input_string.replace('\n', '').replace('\r', '')
    return result_string