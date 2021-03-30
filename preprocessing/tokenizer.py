import jieba
import collections


def word_level_tokenizer(msgs, freq_threshold=5):
    """Tokenizes messages into words, using jieba.

    Keyword Arguments:
    mesgs -- A list of Messages
    freq_threshold -- Threshold to drop rare words (default: 5)

    Returns:
    tokenized words, word frequency, word2index, index2word
    """
    strs = [word for msg in msgs for word in jieba.cut(msg + '\n')]
    word_list = sorted(set(strs))
    word_freq = collections.Counter(strs)
    word2index = dict()
    for word in word_list:
        if word_freq < freq_threshold:
            continue
        else:
            word2index[word] = len(word2index)
    index2word = {v: k for k, v in word2index.items()}

    return strs, word_freq, word2index, index2word


def character_level_tokenizer(msgs, freq_threshold=5):
    raise NotImplementedError('明天再写')
