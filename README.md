# YCTA spider
Tools designed to fetch, store and disseminate data.
___
## Installation

1. ```git clone git@github.com:unnamed16/ycta_spider.git```
2. ```cd ycta_spider```
3. ```git submodule update --recursive --init```
4. ```pip3 install .```

You should have access to global network to use pip.
Python 3.9+ is required.

___
## Usage

This project can be used via _Command Line Interface_, or
it can be included into any other Python project as a submodule.

### Command Line Interface

***info***

Use this command if you want to obtain sources info from the specified platform

```bash
python cli.py info [-h]
                   [-l LIMIT]
                   [-o OUTPUT]
                   platform
```

Positional arguments:

**platform** - platform that has to be processed
[currently only YOUTUBE,
with ambitions to expand to other platforms].

Optional arguments:

**-l**, **--limit** LIMIT - 
limit of the records obtained per source, update infinitely on Enter key if not specified.

**-o**, **--output** OUTPUT - 
where to store the result (url - send, file - save, print if not specified) 

**-h**, **--help** - show this help message and exit


```bash
python cli.py info YOUTUBE
```

```bash
python cli.py info --output C:/result.json YOUTUBE
```

```bash
python cli.py info --output https://myDataBaseServer.com --limit 10 YOUTUBE
```

---

***crawl***

Use this command if you want to obtain comments from the specified platform

```bash
python cli.py crawl [-h]
                    [-l LIMIT]
                    [-o OUTPUT]
                    platform
```

Positional arguments:

**platform** - platform that has to be processed

Optional arguments:

**-l**, **--limit** LIMIT - 
limit of the records obtained per source, update infinitely on Enter key if not specified.

**-o**, **--output** OUTPUT - 
where to store the result (url - send, file - save, print if not specified) 

**-h**, **--help** - show this help message and exit


```bash
python cli.py crawl YOUTUBE
```

```bash
python cli.py crawl --output C:/result.json YOUTUBE
```

```bash
python cli.py crawl --output https://myDataBaseServer.com --limit 10 YOUTUBE

```

---

***highlight***

Use this command if you want to obtain highlighted comments

```bash
python cli.py highlight [-h]
                        [-l LIMIT]
                        [-o OUTPUT]
                        platform
```

Positional arguments:

**platform** - platform that has to be processed

Optional arguments:

**-l**, **--limit** LIMIT - 
limit of the records obtained per source, update infinitely on Enter key if not specified.

**-o**, **--output** OUTPUT - 
where to store the result (url - send, file - save, print if not specified) 

**-h**, **--help** - show this help message and exit


```bash
python cli.py highlight YOUTUBE
```

```bash
python cli.py highlight --output C:/result.json YOUTUBE
```

```bash
python cli.py highlight --output https://myDataBaseServer.com --limit 10 YOUTUBE
```

---

***respond***

Use this command if you want to respond highlighted comments

Examples:

```bash
python cli.py respond [-h]
                      [-l LIMIT]
                      [-o OUTPUT]
                      platform
```

Positional arguments:

**platform** - platform that has to be processed

Optional arguments:

**-l**, **--limit** LIMIT - 
limit of the processed highlighted records per source, work infinitely if not specified.

**-o**, **--output** OUTPUT - 
where to store the result (url - send, file - save, print if not specified) 

**-h**, **--help** - show this help message and exit


```bash
python cli.py respond YOUTUBE
```

```bash
python cli.py respond --output C:/result.json YOUTUBE
```

```bash
python cli.py respond --output https://myDataBaseServer.com --limit 10 YOUTUBE
```

___

### Submodule Interface

#### API:

***Shell*** - common interface for _API Shell_.

```python
from ycta_spider.api.shell import Shell


class MyShell(Shell):
    def get_comments(self):
        pass

    def add_comment(self):
        pass

    def add_response(self):
        pass
```

- **get_comments** - get list of comments at the given source.
- **add_comment** - add comment to the source.
- **add_response** - add response to the specified comment.

***YOUTUBE*** - api shell for the _https://youtube.com_ with common shell interface.

```python
from ycta_spider.api.youtube.shell import Shell
```

___

#### Sentiment:

___

#### Chatbot:


---

#### YouTube access (temporary solution)

### Service Owner:

- Create API key on https://console.cloud.google.com/apis/credentials.
- Mark test users on OAuth consent screen of the project, on https://console.cloud.google.com/apis/dashboard. 
- Obtain client secret json file.
  
### Service User:

- Ask owner to be marked as test user on OAuth 2.0.
- As of right now, client secret file belongs to the owner. 
Run the ```api.youtube.shell.Shell.get_authorization_link```
- It will return a link, navigate to it, allow everything, copy the authorization code.
- Use ```api.youtube.shell.Shell.get_access_token``` to obtain access token (only active for 1h):
