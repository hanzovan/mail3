
def strong_password(e):
    # Define a list of special characters
    special_list = [
        "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "[", "]", "{", "}", "?"
    ]
    # Define function variables
    special = 0
    alphabet = 0
    number = 0

    # If any character in user's string match condition, count it
    for i in e:
        if i in special_list:
            special += 1
        if i.isnumeric():
            number += 1
        if i.isalpha():
            alphabet += 1
    
    # Counting
    print(f"Special character: {special}")
    print(f"Alphabet character: {alphabet}")
    print(f"Number: {number}")
    print(f"Total length: {len(e)}")

    # if user's string have at least 1 special, 1 alphabet, 1 number, and at least 6 characters in total, return True, else return False
    if special > 0 and alphabet > 0 and number > 0 and len(e) >= 6:
        return True
    return False
