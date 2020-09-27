# NestedGenerator
Takes nested lists and makes them into fun random outputs. Mostly just a funsies thing.

The config files are where the data is stored that's used for the raondom generation. 
The format isn't too complicated, but there are a fair number of pieces, noted here.

## Header
First off, each choice file needs a header, in the following format:
* Files must begin with a namespace id of the form '[a-zA-Z_]+' on a line by itself.
* Following lines may contain files to import, in the form '$namespace_id:$filename'.
* Next, there must be a blank line.

## Data Lines
After this comes the data for the choices. 
* Each top-level choice must be preceeded by exactly one blank line (hence why one was required after the header).
* Choices are indented to indicate what their parent and sibling choices are.
* Each choice starts with a number, which represents the relative weight of that choice among its siblings.
* The format of a choice is (  )*\d+( [^@\[\]\{\}]*)?

## Symbols
There are various special symbols that allow for more complex generation.
* '$' in the middle of a choice indicates that a choice should be selected from 
the corresponding child (more on this later) and subbed in where the '$' currently sits.
* '@namespace_id' means that a choice should be rolled from the top level of the given namespace id, and subbed in.

## Uniqueness
The generator has a concept of uniqueness, which allows you to avoid getting multiple of the same result. The uniqueness is keyed off of a
'uniqueness_level' parameter, which specifies at what level results should be unique. 1 is top-level, so no two results may begin at the same top-level
choice. 2 is the level below that, so multiple results could begin at the same top-level choice, but could not then choose an option within that top-level
choice that had previously been chosen.

0 and -1 are special values, representing 'no uniqueness' and 'leaf-level', respectively. Leaf-level uniquenesssimply means that no two entirely identical values 
will result.

## Multiple Sub-namespace Calls
It's possible to request multiple values from a referenced namespace within a single choice, allowing for use to be made of the uniqueness ability. This is done
as follows:
* The format for requesting multiple values is '@namespace_id[N,U]'
  * N is the number of results desired
  * U is the uniqueness_level described in the last section
* To use Nth result in a choice, after it has been requested with the above syntax, the format is '@\d+namespace', where \d+ would be replaced by N.

For example, '@house_colors[5,0]' would request five house colors, without any uniqueness constraints, and replace the token with the first result.
The token '@2house_colors' would then be used to request substitution of the second result, '@3house_colors' for the third, and so on and so forth.

## Random Number Generation
It's possible to generate random numbers inside a choice. The format is '\[\d+-\d+[NG]?\]'. If neither N or G is supplied, then the first number is the min,
the second the max, and the generator will choose an integer between them, inclusively, in a uniform and random manner.

If N is supplied, the first number instead is the mean, the second the standard deviation, and the generator samples from a gaussian distribution with these
parameters before rounding down to the nearest integer.

If G is supplied, it is much like N, except that the first and second numbers correspond to the alpha and beta parameters of the gamma distribution instead.
    
## Randomly Repeated Sub-namespace Calls (RRSNC)
It's also possible to randomly choose how many calls to make to a specified sub-namespace. The format for that is '\[\d+-\d+,\d+\]', which is alsmost the same
as the standard call, with the exception that the first parameter is now a range. That range will be sampled over uniformly, as with the non-NG RNG above.

For example, '@house_colors[3-5,-1]' would generate between 3 and 5 random house colors, and ensure that each value was unique.

## Sub-namespace Clauses
If you want to use RRSNC, you need a way to remove any text in a choice that may have been associated with a sub-namespace call that was not made. To do this,
surround any sub-namespace calls that you are not sure will be made with curly brackets. ('{' and '}') If the call is not made, everything between the brackets
will be removed. If the call is made, only the brackets themselves will be removed.

For example, if a call to 'First color: @house_colors[1-2,-1].{ Second color: @2house_colors.}' only retrieved one house color value, the result might be,
'First color: Green.' If it retrieved both, the result might be, 'First color: Red. Second color: Purple.'

## Multiple Replacement Tokens in a Choice
It is possible to have multiple replacement tokens ('$') in a single choice. The choices for the first token must be separated from the choices for the
second token by a '$' with the same level of indentation as the choices. (If you want to draw from the same pool for both, you can put your choices in a
namespace, and then reference that before and after the '$' separator.

For example, this is a valid three-replacement config:
```
10 My $ fights with my $!
  10 Dog
  5 Cat
  $
  10 Mouse
  5 Fish
```

## Empty Replacement Tokens
It is valid to have a replacement token with no text, and only a weight. This can be useful to, e.g., randomly choose between adding an extra clause onto a
choice, or leaving it as is.
    
## Examples
An example file, demonstrating many of these features, is present in test_places.txt. (Note that this test file also tests some code functions, specifically
constructing a namespace manually, so there is currently no file for @countries_table, as it is dynamically created.)
