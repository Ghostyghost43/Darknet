#!/usr/bin/env python3
"""
Personal Wordlist Generator
Generates targeted wordlists based on personal information about the target
"""

import itertools
from datetime import datetime
from pathlib import Path

try:
    from colorama import Fore, Style
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = WHITE = RESET = ""
    class Style:
        BRIGHT = RESET_ALL = ""


class WordlistGenerator:
    def __init__(self):
        self.info = {}
        self.wordlist = set()

    def ask_questions(self):
        """Ask personal questions about the target"""
        print(f"\n{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║      PERSONAL INFORMATION WORDLIST GENERATOR            ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}[*] Answer questions about the target to generate a custom wordlist{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Press Enter to skip any question{Style.RESET_ALL}\n")

        questions = {
            'first_name': 'Target\'s first name',
            'last_name': 'Target\'s last name',
            'nickname': 'Nickname or alias',
            'spouse_name': 'Spouse/Partner name',
            'child_name': 'Child\'s name (comma-separated if multiple)',
            'pet_name': 'Pet name (comma-separated if multiple)',
            'birth_year': 'Birth year (YYYY)',
            'birth_date': 'Birth date (DDMM or MMDD)',
            'anniversary': 'Anniversary date (DDMM or MMDD)',
            'phone': 'Phone number (last 4-8 digits)',
            'address_number': 'Street address number',
            'city': 'City name',
            'company': 'Company/Employer name',
            'school': 'School/University name',
            'hobby': 'Hobby or interest',
            'favorite_team': 'Favorite sports team',
            'favorite_color': 'Favorite color',
            'car_model': 'Car model',
        }

        for key, question in questions.items():
            answer = input(f"{Fore.CYAN}[?] {question}: {Style.RESET_ALL}").strip()
            if answer:
                # Handle comma-separated values
                if ',' in answer:
                    self.info[key] = [x.strip() for x in answer.split(',')]
                else:
                    self.info[key] = answer

        print(f"\n{Fore.GREEN}[✓] Information collected{Style.RESET_ALL}\n")

    def generate_variations(self, word):
        """Generate variations of a word"""
        if not word:
            return []

        variations = [
            word.lower(),
            word.upper(),
            word.capitalize(),
            word.lower().replace(' ', ''),
            word.upper().replace(' ', ''),
            word.capitalize().replace(' ', ''),
        ]

        return variations

    def generate_combinations(self):
        """Generate password combinations from collected info"""
        print(f"{Fore.CYAN}[*] Generating wordlist from personal information...{Style.RESET_ALL}")

        # Extract all values
        names = []
        dates = []
        numbers = []
        misc = []

        # Process collected information
        for key, value in self.info.items():
            if isinstance(value, list):
                for v in value:
                    if key in ['first_name', 'last_name', 'nickname', 'spouse_name']:
                        names.extend(self.generate_variations(v))
                    elif key in ['child_name', 'pet_name']:
                        names.extend(self.generate_variations(v))
                    elif key in ['city', 'company', 'school', 'hobby', 'favorite_team', 'favorite_color', 'car_model']:
                        misc.extend(self.generate_variations(v))
            else:
                if key in ['first_name', 'last_name', 'nickname', 'spouse_name']:
                    names.extend(self.generate_variations(value))
                elif key in ['birth_year', 'birth_date', 'anniversary']:
                    dates.append(value)
                elif key in ['phone', 'address_number']:
                    numbers.append(value)
                elif key in ['city', 'company', 'school', 'hobby', 'favorite_team', 'favorite_color', 'car_model']:
                    misc.extend(self.generate_variations(value))

        # Add base words
        for word in names + misc:
            self.wordlist.add(word)

        # Add numbers alone
        for num in dates + numbers:
            self.wordlist.add(str(num))

        # Common patterns: name + number
        for name in names:
            for num in dates + numbers:
                self.wordlist.add(f"{name}{num}")
                self.wordlist.add(f"{num}{name}")
                self.wordlist.add(f"{name}_{num}")
                self.wordlist.add(f"{num}_{name}")

        # Name combinations
        if len(names) >= 2:
            for combo in itertools.combinations(names[:10], 2):  # Limit combinations
                self.wordlist.add(f"{combo[0]}{combo[1]}")
                self.wordlist.add(f"{combo[0]}_{combo[1]}")
                self.wordlist.add(f"{combo[1]}{combo[0]}")

        # Add common suffixes
        common_suffixes = ['123', '!', '@', '#', '1', '12', '2024', '2025', '123!', '!123']
        for word in list(names[:20]):  # Limit to avoid explosion
            for suffix in common_suffixes:
                self.wordlist.add(f"{word}{suffix}")

        # Add common prefixes
        common_prefixes = ['i', 'I', 'my', 'My']
        for word in list(names[:20]):
            for prefix in common_prefixes:
                self.wordlist.add(f"{prefix}{word}")
                self.wordlist.add(f"{prefix}love{word}")
                self.wordlist.add(f"{prefix}Love{word}")

        # Date variations
        for date in dates:
            # Add reversed
            self.wordlist.add(date[::-1])

            # Add with separators
            if len(date) == 4:  # MMDD or DDMM
                self.wordlist.add(f"{date[:2]}/{date[2:]}")
                self.wordlist.add(f"{date[:2]}-{date[2:]}")

        # Special combinations with birth year
        if 'birth_year' in self.info:
            year = self.info['birth_year']
            for name in names[:10]:
                self.wordlist.add(f"{name}{year}")
                self.wordlist.add(f"{name}{year[-2:]}")

        # Add leet speak variations for common words
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        for word in list(names[:15]):
            leet_word = word.lower()
            for char, num in leet_map.items():
                leet_word = leet_word.replace(char, num)
            if leet_word != word.lower():
                self.wordlist.add(leet_word)
                self.wordlist.add(leet_word.capitalize())

        # WiFi specific patterns
        wifi_patterns = ['wifi', 'password', 'router', 'network', 'wireless', 'home', 'internet']
        for pattern in wifi_patterns:
            self.wordlist.add(pattern)
            for name in names[:5]:
                self.wordlist.add(f"{name}{pattern}")
                self.wordlist.add(f"{pattern}{name}")
            for num in dates[:3] + numbers[:3]:
                self.wordlist.add(f"{pattern}{num}")

        # Keyboard patterns near names
        keyboard_patterns = ['qwerty', 'asdf', 'zxcv', '1qaz', '2wsx']
        for pattern in keyboard_patterns:
            self.wordlist.add(pattern)
            for name in names[:5]:
                self.wordlist.add(f"{name}{pattern}")

        # Remove empty strings and ensure minimum length
        self.wordlist = {w for w in self.wordlist if w and len(w) >= 4}

    def save_wordlist(self, filename):
        """Save generated wordlist to file"""
        output_file = Path(filename)

        # Sort by length and alphabetically
        sorted_words = sorted(self.wordlist, key=lambda x: (len(x), x))

        with open(output_file, 'w') as f:
            for word in sorted_words:
                f.write(f"{word}\n")

        print(f"{Fore.GREEN}[✓] Wordlist saved: {output_file}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Total passwords: {len(self.wordlist)}{Style.RESET_ALL}")

        # Show sample
        print(f"\n{Fore.CYAN}[*] Sample passwords (first 20):{Style.RESET_ALL}")
        for word in sorted_words[:20]:
            print(f"    {word}")

        if len(sorted_words) > 20:
            print(f"    ... and {len(sorted_words) - 20} more")

        return output_file

    def interactive_mode(self, output_file="wordlists/personal_wordlist.txt"):
        """Run interactive wordlist generation"""
        self.ask_questions()

        if not self.info:
            print(f"{Fore.YELLOW}[!] No information provided{Style.RESET_ALL}")
            return None

        self.generate_combinations()
        return self.save_wordlist(output_file)


def main():
    """Standalone mode"""
    generator = WordlistGenerator()
    generator.interactive_mode()


if __name__ == '__main__':
    main()
