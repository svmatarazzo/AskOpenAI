
import openai
import sys
import csv
import os

openai.api_key = "your-api-key-here"

# Function to get the data from the beginning of the CSV file
def get_csv_data(filepath):
    with open(filepath, newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = [next(reader, None)]  # Get the header
        for i in range(20):  # Get the first 20 rows of data (adjust as necessary)
            row = next(reader, None)
            if row:
                data.append(row)
        return data

def main():
    if len(sys.argv) < 2:
        print("Usage: ask [-t topic] [-g csv_file_path] Your message here")
        sys.exit(1)

    # Initialize with default system message
    system_message = "You are a helpful assistant."

    # Check for the -t flag
    if '-t' in sys.argv:
        topic_index = sys.argv.index('-t')
        if topic_index + 1 < len(sys.argv):  # Ensure there's a topic after -t
            topic = sys.argv[topic_index + 1]
            system_message = f"You are a helpful assistant in all things regarding {topic}."
            # Remove the -t flag and topic from sys.argv
            del sys.argv[topic_index:topic_index+2]
        else:
            print("Error: Missing topic after -t flag.")
            sys.exit(1)

    # Check for the -g flag
    csv_data = None
    if '-g' in sys.argv:
        index = sys.argv.index('-g')
        if index < len(sys.argv) - 1:
            filepath = sys.argv[index + 1]
            csv_data = get_csv_data(filepath)
            if csv_data:
                csv_data_str = " ".join([", ".join(row) for row in csv_data])  # Convert CSV data to string
                filename = filepath.split('/')[-1]  # Get the file name from the file path
                user_message_content = (f"I have a dataset in a file named '{filename}'. Here is an example of what the data looks like, as shown below:"
                                        f"{csv_data_str}"
                                        f"I want you to create a Python script to import this CSV file (named '{filename}') and visualize this data using Seaborn, and then save a PNG of the visualization. Don't include any commentary or instructions, only the Python code. Do not include a code block or backticks.")
                # Remove the -g flag and filepath from sys.argv
                del sys.argv[index:index+2]
            else:
                print("Error: Could not read data from CSV file")
                sys.exit(1)
        else:
            print("Error: No file path specified after -g")
            sys.exit(1)
    else:
        user_message_content = ' '.join(sys.argv[1:])

    # Check for the -sys flag
    if '-sys' in sys.argv:
        sys_index = sys.argv.index('-sys')
        if sys_index + 1 < len(sys.argv):  # Ensure there's a request after -sys
            # Concatenate everything that comes after -sys into a single string
            user_request = ' '.join(sys.argv[sys_index + 1:])
            
            # Determine the user's operating system and terminal
            user_os = os.name
            if user_os == 'posix':
                user_os = 'Linux/Mac'
            elif user_os == 'nt':
                user_os = 'Windows'
            
            # Formulate the question for the API
            user_message_content = f"You must complete this request '{user_request}' and it must be able to run in terminal or its equivalent on {user_os} by simply copying and pasting the response. The person who requested knows what they are doing so they need no warnings about running scripts. Make sure you use any file or folder name they specify in the script if applicable. and any path they specify, if applicable"
            
            # Remove the -sys flag and user_request from sys.argv
            del sys.argv[sys_index:sys_index+2]
            
            # Set messages without system message for -sys
            messages = [{"role": "user", "content": user_message_content}]
        else:
            print("Error: Missing request after -sys flag.")
            sys.exit(1)
    else:
        user_message_content = ' '.join(sys.argv[1:])

        # Set messages with system message for other flags
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message_content}
        ]

    try:
        completion = openai.ChatCompletion.create(
          model="gpt-4-0613",
          messages=messages
        )
        print(completion.choices[0].message['content'])
    except openai.error.OpenAIError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
