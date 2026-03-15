Models are stores in models/ folder.

Namely:

| Id | Name | Year | Download Link | Description Link |
|----|------|------|---------------|------------------|
| w-1 | (Jedi) Traffic collected from servers in a major US metro predominantly serving web traffic | 2025 | [Link](https://drive.google.com/file/d/14H63ERY5fP1faJGXX18D7bSn-zV6l4dP/view?usp=drive_link) | [Description](https://github.com/UMass-LIDS/Jedi) |
| w-2 | (Jedi) Traffic collected from servers in a major EU metro predominantly serving web traffic | 2025 | [Link](https://drive.google.com/file/d/14fygRkql8gzsC5-7xZkqu2EE0srsnES-/view?usp=sharing) | [Description](https://github.com/UMass-LIDS/Jedi) |
| wiki-t-10 | (Wikipedia) Text (HTML pageview) web requests from one CDN cache server of Wikipedia | 2019 | [Link](https://analytics.wikimedia.org/published/datasets/caching/2019/text/cache-t-10.gz) | [Description](https://wikitech.wikimedia.org/wiki/Data_Platform/Data_Lake/Traffic/Caching) |
| docker-lon-02 | (Docker Registry) Post-processed HTTP request logs from an IBM docker registry, London data center | 2017 | [Link](https://iotta.snia.org/traces/static) | [Description](https://people.cs.vt.edu/~butta/docs/fast2018-dockerAnalysis.pdf) |
| letapartika | (Letapartika.lv) Nginx request logs from Letapartika.lv API | 2026 | \[Private\] | - |


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

***Docker Registry** model files has this table structure


| Column Name | Data Type | Notes |
|-------------|-----------|-------|
| timestamp | int | Seconds since Unix epoch |
| http.request.uri | bigint | Unique identifier for the requested URI |
| http.response.written | int | Size of the response written in bytes |
| http.request.duration | double | Duration of the HTTP request in seconds |


Example:
```
1499839367	82249459417699426403655124019487115527	599	1.390729132
1499839206	36088858532669570535396511473532717648	2	0.123273559
1499839261	308135059527064831083608579745542077246	524	0.335124541
1499839257	228516363421568431053664762972341168977	502	1.205622449
1499839317	70440935500587500404130556424458045190	45022	1.737364337
1499839447	176689310272858053013394596072927833185	711	1.40387088
```

**Letapartika.lv** is constructed from privately accessed Nginx logs in a similar manner

| Column Name | Data Type | Notes |
|-------------|-----------|-------|
| timestamp | int | Seconds since Unix epoch |
| uri | bigint | Unique identifier for the requested URI |
| size | int | Size of the response written in bytes |
| response_time | double | Duration of the HTTP request in seconds |

Example:
```
1772760433      103892208721126956789064049409234985069 417     0.083
1772760434      203009079598154224628864646919237337715 883     0.076
1772760434      9250734314564708796703588717689414545   3024    0.157
1772760435      45693763727764759484744725184488196490  1198    0.102
1772760436      132386750707557126347141531310942055986 1508    0.091
```
