import re
import pandas as pd
import matplotlib.pyplot as plt
# from collections import Counter
# import emoji
# import collections
# import datetime

# Function to parse each message
def _parse_message(message):

    """
    Parses a single chat message string to extract the timestamp, sender, and content.

    Parameters:
        message (str): A string representing a single chat message, formatted as 
                       '[timestamp] sender: message content'.

    Functionality:
        - Uses a regular expression to match the standard chat message format.
        - Extracts and returns the timestamp, sender, and content from the message.
        - If the message does not match the expected format, returns (None, None, None).

    Regular Expression Pattern:
        - `^\[(.*?)\] (.*?): (.*)$`
            - `^\[` and `\]`: Matches the timestamp enclosed in square brackets.
            - `(.*?)`: Captures the content of the timestamp.
            - `(.*?):`: Captures the sender's name followed by a colon.
            - `(.*)$`: Captures the content of the message.

    Example:
        message = "[2023-01-01, 12:00 PM] Alice: Hello, how are you?"
        timestamp, sender, content = _parse_message(message)

        # Output:
        # timestamp: "2023-01-01, 12:00 PM"
        # sender: "Alice"
        # content: "Hello, how are you?"

        # For an invalid message:
        message = "Invalid message format"
        timestamp, sender, content = _parse_message(message)

        # Output:
        # timestamp: None
        # sender: None
        # content: None

    Returns:
        tuple: A tuple containing:
            - timestamp (str): The extracted timestamp from the message.
            - sender (str): The extracted sender's name from the message.
            - content (str): The extracted message content.
            - Returns (None, None, None) if the format does not match.

    Notes:
        - Hidden by convention (name prefixed with an underscore) to indicate it is 
          intended for internal use within a script or module.
        - This function assumes a consistent format for chat messages; unexpected formats 
          may result in (None, None, None).

    """

    pattern = r'^\[(.*?)\] (.*?): (.*)$'
    match = re.match(pattern, message.strip())
    if match:
        timestamp, sender, content = match.groups()
        return timestamp, sender, content
    return None, None, None

def load_chat_data(file_path, split_timestamp = True):

    """
    Loads chat data from a text file, parses the messages, and returns a structured DataFrame. 
    Optionally splits the 'Timestamp' column into separate 'Date' and 'Time' columns.

    Parameters:
        file_path (str): The file path to the chat text file. The file is expected to contain
                         chat messages in a standard format.
        split_timestamp (bool): A flag indicating whether to split the 'Timestamp' column into 
                                separate 'Date' and 'Time' columns. Default is True.

    Functionality:
        - Reads the chat text file line by line.
        - Parses each message using a helper function `_parse_message`.
        - Filters out messages that could not be parsed.
        - Constructs a DataFrame with columns ['Timestamp', 'Sender', 'Content'].
        - Optionally splits the 'Timestamp' column into 'Date' and 'Time' columns using 
          `_split_and_reorder_timestamp` if `split_timestamp` is True.

    Example:
        # Assuming '_chat.txt' contains the chat data
        df = load_chat_data('_chat.txt', split_timestamp=True)

        # Sample output when split_timestamp=True:
        #          Date        Time   Sender             Content
        # 0  2023-01-01  12:00 PM    Alice    Hello, how are you?
        # 1  2023-01-01   1:00 PM      Bob    I'm good, thanks!

        # Sample output when split_timestamp=False:
        #             Timestamp   Sender             Content
        # 0  2023-01-01, 12:00 PM    Alice    Hello, how are you?
        # 1  2023-01-01, 1:00 PM      Bob    I'm good, thanks!

    Returns:
        pd.DataFrame: A DataFrame containing the parsed chat messages, with the structure 
                      determined by the value of `split_timestamp`.

    Notes:
        - The text file must follow a consistent chat format for parsing to work correctly.
        - The helper function `_parse_message` is used to extract message details from each line.
        - If messages fail to parse, they are excluded from the resulting DataFrame.

    Raises:
        FileNotFoundError: If the specified file path does not exist.
        ValueError: If the chat data format is invalid or cannot be parsed.

    """

    # Read chat data from text file
    with open('_chat.txt', 'r', encoding='utf-8') as f:
        chat_data = f.readlines()

    # Parse all messages
    parsed_messages = [_parse_message(message) for message in chat_data]

    # Filter out any messages that failed to parse
    parsed_messages = [msg for msg in parsed_messages if msg[0] is not None]

    # Create a DataFrame
    df = pd.DataFrame(parsed_messages, columns=['Timestamp', 'Sender', 'Content'])  

    if split_timestamp:
        df = _split_and_reorder_timestamp(df)

    return df

# Split the `Timestamp` column into a `date` and a `time` column
def _split_and_reorder_timestamp(df):

    """
    Splits the 'Timestamp' column into separate 'Date' and 'Time' columns 
    and reorders the dataframe columns.

    Parameters:
        df (pd.DataFrame): A dataframe containing a 'Timestamp' column formatted as 
                           'Date, Time', along with other columns such as 'Sender' 
                           and 'Content'.

    Functionality:
        - Splits the 'Timestamp' column into two new columns: 'Date' and 'Time'.
        - Reorders the dataframe columns to ensure the order is ['Date', 'Time', 'Sender', 'Content'].

    Example:
        # Sample dataframe
        data = {
            "Timestamp": ["2023-01-01, 12:00 PM", "2023-01-02, 1:30 PM"],
            "Sender": ["Alice", "Bob"],
            "Content": ["Hello", "Hi"]
        }
        df = pd.DataFrame(data)

        # Split and reorder
        df = _split_and_reorder_timestamp(df)

        # Resulting dataframe
        #      Date        Time   Sender  Content
        # 0  2023-01-01  12:00 PM  Alice    Hello
        # 1  2023-01-02   1:30 PM    Bob      Hi

    Returns:
        pd.DataFrame: The modified dataframe with 'Date' and 'Time' columns, 
                      and columns reordered to ['Date', 'Time', 'Sender', 'Content'].

    Notes:
        - This function assumes the 'Timestamp' column exists and is correctly formatted.
        - Hidden by convention (name prefixed with an underscore) to indicate it is 
          intended for internal use within a script or module.
    """
    
    # Split `Timestamp` column into `Date` and `Time` columns
    df[["Date", "Time"]] = df.Timestamp.str.split(",", expand=True)

    # Reorder columns
    df = df[["Date", "Time", "Sender", "Content"]]

    return df

def plot_senders_distribution(df):

    """
    Plots the distribution of messages by sender from a given chat dataframe.

    Parameters:
        df (pd.DataFrame): A dataframe containing chat data with at least one column named "Sender", 
                           which specifies the sender of each message.

    Functionality:
        - Groups messages by "Sender" and calculates the total number of messages per sender.
        - Plots the distribution as a horizontal bar chart with the number of messages on the x-axis 
          and the senders on the y-axis.
        - Dynamically annotates each bar with its corresponding message count.

    Chart Features:
        - Bars are styled with a "skyblue" fill and "steelblue" edges.
        - Message counts are displayed as annotations near each bar.
        - Includes clear labels for the x-axis ("Number of Messages"), y-axis ("Senders"), 
          and a title ("Distribution of Messages by Sender").

    Example:
        # Sample dataframe
        data = {
            "Date": ["2023-01-01", "2023-01-02", "2023-01-03"],
            "Sender": ["Alice", "Bob", "Alice"],
            "Content": ["Hello world", "Happy New Year", "Hello again!"]
        }
        df = pd.DataFrame(data)

        # Plot the senders' message distribution
        plot_senders_distribution(df)
    
    Notes:
        - Ensure the dataframe contains a "Sender" column for grouping.
        - The function directly displays the plot using matplotlib.

    Returns:
        None
    """

    # Group by "Sender" and get the size of each group
    sender_message_count = df.groupby("Sender").size()
    print(sender_message_count)

    # Create a figure
    plt.figure(figsize=(10, 6))

    # Plot the senders' distribution as a horizontal bar chart
    sender_message_count.plot(kind="barh", color="skyblue", edgecolor="steelblue")

    # Annotate each bar with its corresponding value
    for index, value in enumerate(sender_message_count):
        plt.annotate(f"{value}", 
                    (value, index),  # Position: (x, y)
                    textcoords="offset points",  # Use offset to fine-tune text position
                    xytext=(5, 0),  # Offset text slightly to the right
                    ha='left',  # Align text to the left of the position
                    bbox=dict(boxstyle="round,pad=0.3", fc="lightblue", ec="steelblue", lw=1))

    # Add labels and title for better readability
    plt.xlabel("Number of Messages")
    plt.ylabel("Senders")
    plt.title("Distribution of Messages by Sender", fontsize = 15, fontweight = "medium")


def count_word_usage(word, df):
    """
    Counts how many times a specific word or phrase (message of interest) appears in the chat,
    and returns a dataframe of occurrences with dates and content.

    Parameters:
        word (str): The word or phrase to search for.
        df (pd.DataFrame): The chat dataframe with columns 'Date' and 'Content'.

   Returns:
        pd.DataFrame: A filtered dataframe with the dates and messages containing the word.
    """

    # Filter rows where the content contains the word
    filtered_df = df[df["Content"].str.contains(word, case=False, na=False)]

    # Select relevant columns
    return filtered_df[["Date", "Sender", "Content"]]