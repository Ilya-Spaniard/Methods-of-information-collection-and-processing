import os
import string

punctuation = string.punctuation + '—“”…«»\xa0'
remove_punct_table = str.maketrans('', '', punctuation)

def processing_line(line: str):
    return line.strip().translate(remove_punct_table).lower()

def counting_words(line: str, cnt_words: dict):
    words = line.split()
    for word in words:
        if word in cnt_words:
            cnt_words[word] +=1
        else:
            cnt_words[word] = 1

def write_counted_words(cnt_words_sorted: list):
    output_dir = 'result'
    output_file = 'conted_words.txt'
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, output_file)
    
    with open(file_path, 'w', encoding='utf8') as result:
        for word, cnt in cnt_words_sorted:
            result.write(f'{word} - {cnt}\n')

def main():
    path_book = 'book/book.txt'
    cnt_words = {}

    with open(path_book, 'r', encoding='utf8') as book:
        for line in book:
            line = processing_line(line)
            counting_words(line, cnt_words)  

    cnt_words_sorted = sorted(cnt_words.items(), key=lambda item: item[1], reverse=True)
    write_counted_words(cnt_words_sorted)

if __name__ == '__main__':
	main()
