import ast
import string

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from password import PyPass
from settings import EXCLUDED_WORDS, USABLE_CHARS, EXCLUDED_CHARS, MIN_PASS_LEN, MAX_PASS_LEN, FIXED_LEN
from language import ModelManager

module_name = "Pypass: quickly generate passwords with Python."
__version__ = "0.0.2"


"""
Converts any numbers in a list and its nested lists into a string.
"""


def convert_to_strings(my_list):
    for i in my_list:
        if not isinstance(i, list):
            my_list[my_list.index(i)] = str(i)
        else:
            convert_to_strings(i)
    return my_list


"""
Console implementation of pypass module.
"""

def main():
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                            description=f"{module_name} (Version {__version__})"
                            )

    parser.add_argument("--password_number", "-pn", metavar='NUMBER_OF_PASSWORDS',
                        action="store", dest="number_of_passwords", default="1",
                        help="Number of passwords to be generated."
                        )

    parser.add_argument("--min_len", "-min", metavar='MIN_PASS_LEN',
                        action="store", dest="min_pass_len", default=MIN_PASS_LEN,
                        help="Minimum password length."
                        )

    parser.add_argument("--max_len", "-max", metavar='MAX_PASS_LEN',
                        action="store", dest="max_pass_len", default=MAX_PASS_LEN,
                        help="Maximim password length."
                        )

    parser.add_argument("--fix_len", "-fix", metavar='FIX_PASS_LEN',
                        action="store", dest="fix_pass_len", default=FIXED_LEN,
                        help="Enforces constatnt length of passwords."
                        )

    parser.add_argument("--usable_chars", "-uc", metavar='USER_USABLE_CHARS',
                        action="store", dest="user_usable_chars", default=None,
                        help="A list of characters to be used in password generation."
                             "Can be separated into multiple lists ('[1,2,3],['a','b','c'],[')','_','=']'),"
                             "in which case this will, among other things, influence maintaining proportions."
                             "Using nested lists will cause errors."
                             "If not defined, USABLE_CHARS from settings.py will be used."
                        )

    parser.add_argument("--excluded_chars", "-ec", metavar='USER_EXCLUDED_CHARS',
                        action="store", dest="user_excluded_chars", default=None,
                        help="A list of characters that CANNOT be used in password generation."
                             "Any character listed here will be removed from list(s) of usable characters."
                             "If not defined, EXCLUDED_CHARS from settings.py will be used."
                        )

    parser.add_argument("--excluded_words", "-ew", metavar='USER_EXCLUDED_WORDS',
                        action="store", dest="user_excluded_words", default=None,
                        help="A list of words or other sequences of characters that can't be contained in the password."
                             "Any item from the list will, if found, be removed from the password and replace with a "
                             "random sequence of character from the usable_char list(s)."
                             "If not defined, EXCLUDED_WORDS from settings.py will be used."
                        )

    parser.add_argument("--remove_english", "-re", metavar='REMOVE_ENGLISH',
                        action="store", dest="remove_english", default=False,
                        help="If not False, will cause English words to be removed from the passwords."
                        )

    parser.add_argument("--remove_repeating", "-rr", metavar='REMOVE_REPEATING',
                        action="store", dest="remove_repeating", default=False,
                        help="If not False, will cause touching duplicate characters to be removed from the passwords."
                        )

    parser.add_argument("--ensure_proportions", "-ep", metavar='ENSURE_PROPORTIONS',
                        action="store", dest="ensure_proportions", default=False,
                        help="If not False, the password will contain at least one character from each list "
                             "in usable_chars."
                        )

    parser.add_argument("--human", "-hu",
                        action="store_true", dest="human",
                        help="Module will use generate_human_password() instead of generate_password()."
                             "Only settings usable with this function will be applied."
                        )

    parser.add_argument("--simple", "-sm",
                        action="store_true", dest="simple_mode",
                        help="Activates 'simple' mode. User will be able to change parameters for password length"
                             "and use simple commands to eliminate predefined character groups (numbers, lowercase"
                             ", uppercase and punctuation) from usable_chars."
                             "Password will be generated using generate_password() function."
                        )

    parser.add_argument("--digi", "-dt",
                        action="store_true", dest="digits",
                        help="Reserved for Simple Mode. Removes digits from usable_chars."
                        )

    parser.add_argument("--lower", "-l",
                        action="store_true", dest="lower",
                        help="Reserved for Simple Mode. Removes lower case letters from usable_chars."
                        )

    parser.add_argument("--upper", "-up",
                        action="store_true", dest="upper",
                        help="Reserved for Simple Mode. Removes upper case letters from usable_chars."
                        )

    parser.add_argument("--punct", "-pu",
                        action="store_true", dest="punctuation",
                        help="Reserved for Simple Mode. Removes punctuation from usable_chars."
                        )

    parser.add_argument("--remove_quote", "-rq",
                        action="store", dest="remove_quote",
                        help="Reserved for Simple Mode. Removes single quote << ' >> from usable_chars."
                        )

    parser.add_argument("--lang_lib", "-ll",
                        action="store", dest="lang_lib",
                        help="Designates that the password will be generated as a random sentence, " \
                             "without any whitespace and determines the library to be used for this."
                        )

    parser.add_argument("--incl_wspace", "-iw",
                        action="store", dest="incl_wspace", default=True,
                        help="Determines if whitespaces will be permitted in the natural language passwords."
                        )

    parser.add_argument("--make", "-m",
                        action="store", dest="save_model",
                        help="Generate nltk trigram model."
                        )

    parser.add_argument("--delete", "-d",
                        action="store", dest="delete_model",
                        help="Delete nltk trigram model."
                        )

    args = parser.parse_args()

    if args.save_model and args.delete_model:
        raise ValueError("Cannot both save and delete a model.")

    elif args.delete_model:
        model_name = args.delete_model
        ModelManager(model_name).delete()
        return

    elif args.save_model:
        model_name = args.save_model
        ModelManager(model_name).make_model(source='l')
        return

    pass_no = int(args.number_of_passwords)

    # Raise an exception in case minimum number of chars is greater than the maximum.
    if int(args.min_pass_len) >= int(args.max_pass_len):
        raise Exception("Parameter --min_len/-min must be lower than --max_len/-max.")

    # Will need this one in simple mode and without it.
    if args.fix_pass_len:
        is_fixed = int(args.fix_pass_len)
    else:
        is_fixed = args.fix_pass_len

    # Implementation of the simple mode
    if args.simple_mode:

        if args.digits and args.lower and args.upper and args.punctuation:
            raise Exception("Cannot exclude all usable characters.")

        usable_chars = {
            'lowercase':list(string.ascii_lowercase),
            'uppercase':list(string.ascii_uppercase),
            'digits':list(string.digits),
            'punctuation':list(string.punctuation),
        }

        if args.digits:
            usable_chars.pop('digits')
        if args.lower:
            usable_chars.pop('lowercase')
        if args.upper:
            usable_chars.pop('uppercase')
        if args.punctuation:
            usable_chars.pop('punctuation')
        if args.remove_quote and not args.punctuation:
            usable_chars['punctuation'].remove("'")

        usable_chars = [v for v in usable_chars.values()]

        password_generator = PyPass(usable_chars=usable_chars, excluded_chars=[],
                                    min_pass_len=int(args.min_pass_len), max_pass_len=int(args.max_pass_len),
                                    excluded_words=[])
        password_generator.generate_password(pass_number=pass_no, fixed_len=is_fixed)

    if args.lang_lib is not None:
        password_generator = PyPass(min_pass_len=int(args.min_pass_len), max_pass_len=int(args.max_pass_len), language_lib=args.lang_lib, include_whitespace=ast.literal_eval(args.incl_wspace))
        password_generator.generate_sentence_pass(pass_number=pass_no)

    else:

        if args.user_usable_chars is not None:
            usable_chars = convert_to_strings(list(ast.literal_eval(args.user_usable_chars)))
        else:
            usable_chars = USABLE_CHARS

        if args.user_excluded_chars is not None:
            excluded_chars = convert_to_strings(ast.literal_eval(args.user_excluded_chars))
        else:
            excluded_chars = EXCLUDED_CHARS

        if args.user_excluded_words is not None:
            excluded_words = convert_to_strings(ast.literal_eval(args.user_excluded_words))
        else:
            excluded_words = EXCLUDED_WORDS

        remove_repeating = args.remove_repeating
        remove_english = args.remove_english
        ensure_proportions = args.ensure_proportions

        password_generator = PyPass(usable_chars=usable_chars, excluded_chars=excluded_chars,
                                    min_pass_len=int(args.min_pass_len), max_pass_len=int(args.max_pass_len),
                                    excluded_words=excluded_words, remove_repeating=remove_repeating,
                                    remove_english=remove_english, ensure_proportions=ensure_proportions)

        if args.human:
            password_generator.generate_human_password(pass_number=pass_no, fixed_len=is_fixed)
        else:
            password_generator.generate_password(pass_number=pass_no, remove_repeating=remove_repeating,
                                                 remove_english=remove_english, check_proportions=ensure_proportions,
                                                 fixed_len=is_fixed)

    if len(password_generator.all_passwords) == 1:
        print(password_generator.all_passwords[0])
        return password_generator.all_passwords[0]

    print(password_generator.all_passwords)
    return password_generator.all_passwords

if __name__ == "__main__":
    main()
