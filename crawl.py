import re
import requests
from googlesearch import search
import os
import csv

def find_emails(text):
    email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    potential_emails = email_regex.findall(text)

    cleaned_emails = []
    for email in potential_emails:
        # Remove trailing characters that are not part of an email
        if email[-1] in ['.', ',', ';', ':']:
            email = email[:-1]

        # Further checks to filter out false positives
        if not any(unwanted in email for unwanted in ['%', '!', '#', '&', '?', 'Du']):
            # Filter out emails with uncommonly long local-parts or domains
            local, domain = email.split('@')
            if len(local) < 30 and len(domain) < 30:
                cleaned_emails.append(email)

    return cleaned_emails


def crawl_website(url):
    try:
        response = requests.get(url)
        emails = find_emails(response.text)
        return emails
    except requests.RequestException:
        return []

def google_search(query, num_results=10):
    emails = set()
    count = 0
    for url in search(query):
        if count >= num_results:
            break
        emails.update(crawl_website(url))
        count += 1
    return list(emails)


def read_existing_emails(file_path):
    if not os.path.isfile(file_path):
        return set()
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        return set(row[0] for row in reader if row)

def save_emails_to_csv(emails, file_path):
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for email in emails:
            writer.writerow([email])

def main():
    csv_file_path = 'emails.csv'
    
    while True:  # This starts an infinite loop.
        try:
            existing_emails = read_existing_emails(csv_file_path)
            
            # Prompt the user for a search term
            search_query = input("Please enter the search term (or type 'exit' to quit): ")
            
            if search_query.lower() == 'exit':  # If user types 'exit', break the loop and end the script.
                print("Exiting the program.")
                break
            
            # Use the user's input as the search query
            new_emails = set(google_search(search_query))
            
            # Report the number of emails found
            print(f"Found {len(new_emails)} new emails for the term '{search_query}'.")
            
            # Combine and remove duplicates
            all_emails = existing_emails.union(new_emails)
            
            # Save to CSV
            save_emails_to_csv(all_emails, csv_file_path)
            print(f"Updated list saved to {csv_file_path}. Total unique emails: {len(all_emails)}")
            
        except KeyboardInterrupt:
            # If user hits Ctrl+C, print a message and break the loop.
            print("\nProcess interrupted by user. Exiting.")
            break

if __name__ == "__main__":
    main()



