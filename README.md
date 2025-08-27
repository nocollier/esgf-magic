
# esgf-magic

I have an idea for a utility that would be able to look at a CV database and then allow a user to simply type terms:

```
CESM2 historical gpp tas mon
```

and the tool would yield:

```
project="CMIP6",
source_id="CESM2",
experiment_id="historical",
variable_id=["gpp", "tas"],
frequency="mon"
```

But if you typed

```
CESM* tas historical mon
```

you would techincally see 2 possibilities:

```
project="CMIP5",
model=["CESM1(CAM5)", "CESM1(WACCM)"],
experiment="historical",
variable="tas",
time_frequency="mon"
```

and 

```
project="CMIP6",
source_id=['CESM2-FV2', 'CESM2-WACCM-FV2', 'CESM2-WACCM', 'CESM2'],
experiment_id="historical",
variable_id="tas",
frequency="mon"
```

Ideally the tool would guess at which result you want. 

Note that this would *not* query any index, but build the possible searches from the CVs themselves. This way the user does not need to know what facets to type.

## Behavior

- The tool should be permissive, by default omitting terms which were not found or used.
- There should be an option `--error-on-leftover` in case the user wants to make sure all terms were used.
- The tool should accept wildcards in the search terms
- The tool should allow for different output formats (python, json, REST API)
- When multiple projects have partial matches to the terms given, the one with the most terms should be returned. In the case of ties, the most recent project is returned.
- The tool should be fast so that it can be inserted into others with minimal interruption. Python is fine but if need be, it could be written in Rust.
- This could be a good precursor for a chatbot to help build searches from words that it finds are ESGF terms
