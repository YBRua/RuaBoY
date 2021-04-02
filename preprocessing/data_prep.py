import random


def data_loader(sentence, word2index, seg_length):
    """Yields one (x,y) pair of training data

    Keyword Arguments:
    sentence -- A list of all training data
    word2index -- Mapping from word to index
    seg_length -- length of a sample

    Returns:
    one pair of (x, y).
    """
    while True:
        index = random.randint(0, len(sentence)-(seg_length-2))
        segment_x = sentence[index: index + seg_length]
        x = [
            word2index[word] if word in word2index
            else word2index['__unk__']
            for word in segment_x]
        segment_y = sentence[index + 1: index + seg_length + 1]
        y = [
            word2index[word] if word in word2index
            else word2index['__unk__']
            for word in segment_y]

        yield x, y


def batch_data_loader(sentence, word2index, seg_length, batch_size):
    """Yields a batch of (x, y) data.

    Keyword Arguments:
    sentence -- a list of all training data
    word2index -- a mapping from word to index
    seg_length -- length of a sample
    batch_size -- size of a batch, i.e. how many (x, y) pairs in each batch

    Returns:
    A list of x and a list of corresponding y
    """
    while True:
        batch_x = []
        batch_y = []
        single_loader = data_loader(sentence, word2index, seg_length)
        for i in range(batch_size):
            x, y = next(single_loader)
            batch_x.append(x)
            batch_y.append(y)

        yield batch_x, batch_y
