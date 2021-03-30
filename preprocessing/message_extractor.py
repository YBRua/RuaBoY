
# %%
import collections
import typing
import datetime
import re

UserInfo = collections.namedtuple(
    'UserInfo',
    ['username', 'uid'])


class Message:
    def __init__(self, dt, uid, msg):
        self.datetime = dt
        self.user_info = uid
        self.message = msg


class MessageExtractor:
    def __init__(self, path='', show_every_lines=-1, verbose=False):
        self.path = path
        self.debug = verbose
        self.show_every_line = show_every_lines
        self._pointer = 0
        self.line = 1
        self._pause_char = '\0'
        self.message_boxes = []
        self._buffer = '\0'
        if path != '':
            self._read_file()

    def _read_file(self):
        with open(self.path, 'r', encoding='utf-8-sig') as f:
            self._buffer = f.read().replace('\r', '') + '__EOF__\n'
        self._lookahead = self._scan()

    def _scan(self):
        word_list = []
        while (self._buffer[self._pointer] == ' '
                or self._buffer[self._pointer] == '\n'):
            if self._pointer == len(self._buffer) - 1:
                return ''
            if self._buffer[self._pointer] == '\n':
                self.line += 1
            self._pointer += 1
        while (self._buffer[self._pointer] != ' '
                and self._buffer[self._pointer] != '\n'):
            word_list.append(self._buffer[self._pointer])
            self._pointer += 1
        self._pause_char = self._buffer[self._pointer]
        current_word = ''.join(word_list)

        if self.debug:
            print(
                '[MessageExtractor]:',
                'Scanned word\nLine:', self.line,
                '\nContent:', current_word,
                '\nPaused at:', repr(self._pause_char))
        if self.show_every_line != -1:
            if self.line % self.show_every_line == 0:
                print('[MessageExtractor]: At line', self.line)

        if self._buffer[self._pointer] == '\n':
            self.line += 1
            self.column = 0
        self._pointer += 1
        return current_word

    def _match(self, s):
        if self._lookahead == s:
            self._lookahead = self._scan()
            return
        else:
            raise ValueError(
                '\n[MessageExtractor] Error extracting file:\n'
                + ' At line: ' + str(self.line)
                + '.\nExpected:\n  ' + s + '\nGot:\n  ' + self._lookahead)

    def _parse_datetime(self):
        datetime_string = self._lookahead
        self._match(self._lookahead)
        datetime_string = datetime_string + ' ' + self._lookahead

        if self.debug:
            print(
                '[MessageExtractor]: Extracted datetime:',
                datetime_string + '\n')
        dt = datetime.datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        self._match(self._lookahead)
        return dt

    def _parse_uid(self):
        uid_list = [self._lookahead]
        username = ''
        uid = ''
        while self._pause_char != '\n':
            self._match(self._lookahead)
            uid_list.append(self._lookahead)
        uid_string = ''.join(uid_list)
        # username(UID)
        val = re.search('[(][0-9]*[)]', uid_string)
        if val:
            uid = val.group(0).replace('(', '').replace(')', '')
            username = re.split('[(][0-9]*[)]', uid_string)[0]
        # username<mail>
        val = re.search('<.*>', uid_string)
        if val:
            uid = val.group(0).replace('<', '').replace('>', '')
            username = re.split('<.*>', uid_string)[0]
        # username only
        if username == '':
            username = uid_string

        if self.debug:
            print('[MessageExtractor]: Extracted user info:', username + '\n')
        self._match(self._lookahead)
        return UserInfo(username, uid)

    def _parse_message(self):
        msg_segment = []
        while not re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', self._lookahead):
            if self._lookahead == '__EOF__':
                break
            msg_segment.append(self._lookahead)
            # concat all characters in the message
            self._match(self._lookahead)

        if self.debug:
            print('[MessageExtractor]: Extracted message.' + '\n')
        return ''.join(msg_segment)

    def _parse_chatbox(self):
        dt = self._parse_datetime()
        uid = self._parse_uid()
        msg = self._parse_message()
        return Message(dt, uid, msg)

    def _parse_chatboxes(self):
        while self._lookahead != '__EOF__':
            self.message_boxes.append(self._parse_chatbox())

    def _parse_filehead(self):
        # skip all useless fileheads
        while not re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}', self._lookahead):
            self._match(self._lookahead)

    def extract(self, path='') -> typing.List[Message]:
        """Extract chat messages.
        Convert chat records txt files into a list of chat messages.

        Returns
        ---
        A list of chat messages.
        """
        if path != '':
            self.change_path(path)
        if self._buffer == '\0':
            raise ValueError('[MessageExtractor]: Nothing to extract.')
        print('[MessageExtractor]: Extracting chat messages...')
        self.message_boxes = []
        self._parse_filehead()
        self._parse_chatboxes()
        print('[MessageExtractor]: File successfully extracted.')
        return self.message_boxes

    def change_path(self, path):
        """Change .txt file path
        Change the path to .txt chat record.
        """
        self.path = path
        self._read_file()

    def drop_bad_data(self) -> typing.List[Message]:
        # TODO: Drop '系统消息'
        """Further process extracted message.
        Drops @Somebody and [图片].
        """
        print('[MessageExtractor]: Dropping bad data...')
        if self.message_boxes:
            self.message_boxes = [
                msg for msg in self.message_boxes
                if (not re.match(r'.*\[.*\].*', msg.message))
                and (not re.match(r'.*@.*', msg.message))]
        else:
            print('[MessageExtractor]: Cannot drop bad data. List is empty.')
            return []
        print('[MessageExtractor]: Bad data successfully dropped.')
        return self.message_boxes

    def to_csv(self, path='output.csv'):
        """Output to .csv file.
        Outputs current message list to a .csv file.
        """
        print('[MessageExtractor]: Outputing to .csv file...')
        if self.message_boxes:
            with open(path, 'w', encoding='utf-8-sig') as f:
                f.write('datetime,uid,username,message\n')
                for r in self.message_boxes:
                    f.write(
                        r.datetime.strftime('%Y-%m-%d %H:%M:%S') + ','
                        + r.user_info.uid + ','
                        + r.user_info.username + ','
                        + r.message + '\n')
            print('[MessageExtractor]: Successfully outputted to', path)
        else:
            print('[MessageExtractor]: Cannot output. List is empty.')
