string = "hello/there/mister"
string2 = "Hello:there:misses"
string3 = "Hello"


def get_delimiter(string: str) -> str | None:
    if any((match := delimiter) in string for delimiter in [":", "/"]):
        return match
    else:
        return None


for test_string in [string, string2, string3]:
    print(get_delimiter(test_string))
