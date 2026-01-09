Models are stores in models/ folder.

Namely:

| Id | Name | Year | Download Link | Description Link |
|----|------|------|---------------|------------------|
| w-1 | (Jedi) Traffic collected from servers in a major US metro predominantly serving web traffic | 2025 | [Link](https://drive.google.com/file/d/14H63ERY5fP1faJGXX18D7bSn-zV6l4dP/view?usp=drive_link) | [Description](https://github.com/UMass-LIDS/Jedi) |
| w-2 | (Jedi) Traffic collected from servers in a major EU metro predominantly serving web traffic | 2025 | [Link](https://drive.google.com/file/d/14fygRkql8gzsC5-7xZkqu2EE0srsnES-/view?usp=sharing) | [Description](https://github.com/UMass-LIDS/Jedi) |
| wiki-t-10 | (Wikipedia) Text (HTML pageview) web requests from one CDN cache server of Wikipedia | 2019 | [Link](https://analytics.wikimedia.org/published/datasets/caching/2019/text/cache-t-10.gz) | [Description](https://wikitech.wikimedia.org/wiki/Data_Platform/Data_Lake/Traffic/Caching) |


**Jedi** model files follow this structure:
```
timestamp, object_id, object_size (KB)
1532702631,0,26624
1532702631,1,12288
1532702631,2,26624
1532702631,3,26624
....
```

**Wikipedia** model files has this table structure

| Column Name | Data Type | Notes |
|-------------|-----------|-------|
| relative_unix | int | Seconds since start timestamp of dataset |
| hashed_host_path_query | bigint | Salted hash of host, path, and query of request |
| response_size | int | Response size in bytes |
| time_firstbyte | double | Seconds to first byte |

Example:
```
relative_unix   hashed_host_path_query  response_size   time_firstbyte
864000  1714473446      20546   2.8E-4
864000  -889152392      17446   1.88E-4
864000  -609074327      34912   1.83E-4
...
```
