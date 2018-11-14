# janes-standardictor

Tool for predicting the level of linguistic and technical standardness of a Slovene utterance.

## Dependencies

python2.7

sklearn 0.17 (newer versions might / should work)

## Usage

For each line from standard input, estimates of technical and linguistic non-standardness (1-3, less being more standard) are written to the standard output.

```
$ cat example.txt | python janes-standardictor.py 
2.4	2.2
1.1	1.1
```
