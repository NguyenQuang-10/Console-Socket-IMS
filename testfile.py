import re
string = "!USN! #fuck"
usn_format = re.compile(r"^!USN!\s\w+$")
check = usn_format.findall(string)
print(check)
if len(check) == 1:
    print("True")