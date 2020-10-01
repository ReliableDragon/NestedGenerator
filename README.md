# NestedGenerator
Takes nested lists and makes them into fun random outputs. Mostly just a funsies thing.

The config files are where the data is stored that's used for the random generation.
The format isn't too complicated, but there are a fair number of pieces, noted here.

## Header
First off, each choice file needs a header, in the following format:
* Files must begin with a namespace id of the form '[a-zA-Z_]+' on a line by itself.
* Following lines may contain files to import, in the form '$namespace_id:$filename'.
* Next, there must be a blank line.

## Data Lines
After this comes the data for the choices.
* Each top-level choice must be preceded by exactly one blank line (hence why one was required after the header).
* Choices are indented to indicate what their parent and sibling choices are.
* Each choice starts with a number, which represents the relative weight of that choice among its siblings.
* The format of a choice is (  )*\d+( [^@\[\]\{\}]*)?

## Symbols
There are various special symbols that allow for more complex generation.
* '$' in the middle of a choice indicates that a choice should be selected from
the corresponding child (more on this later) and subbed in where the '$' currently sits.
* '@namespace_id' means that a choice should be rolled from the top level of the given namespace id, and subbed in.

An example:
```
10 $ Coin
  10 Copper
  5 Silver
  1 Gold

2 Chest filled with $
  10 gold
  5 gems
  1 magic items
```

## Uniqueness
The generator has a concept of uniqueness, which allows you to avoid getting multiple of the same result. The uniqueness is keyed off of a
'uniqueness_level' parameter, which specifies at what level results should be unique. 1 is top-level, so no two results may begin at the same top-level
choice. 2 is the level below that, so multiple results could begin at the same top-level choice, but could not then choose an option within that top-level
choice that had previously been chosen.

0 and -1 are special values, representing 'no uniqueness' and 'leaf-level', respectively. Leaf-level uniqueness simply means that no two entirely identical values
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

It's possible to store the result of the random number generation into a state, by appending %STATE_NAME% just before the closing bracket, like so:
```
[1-10G%random_number%]
```
For more on state, see below.

## Randomly Repeated Sub-namespace Calls (RRSNC)
It's also possible to randomly choose how many calls to make to a specified sub-namespace. The format for that is '\[\d+-\d+,\d+\]', which is almost the same
as the standard call, with the exception that the first parameter is now a range. That range will be sampled over uniformly, as with the non-NG RNG above.

For example, '@house_colors[3-5,-1]' would generate between 3 and 5 random house colors, and ensure that each value was unique.

## Bracket Clauses
When writing a choice where an element may not be present (such as when randomly repeating a sub-namespace call above), you need a way to remove any text in a choice that may have been associated with the element that was not present. To do this, surround the conditional item that you are not sure will be present with curly brackets. ('{' and '}') If the item is not present, everything between the brackets
will be removed. If it is present, only the brackets themselves will be removed.

For example, if a call to 'First color: @house_colors[1-2,-1].{ Second color: @2house_colors.}' only retrieved one house color value, the result might be, 'First color: Green.' If it retrieved both, the result might be, 'First color: Red. Second color: Purple.'

Bracket clauses are supported for RRSNC, and state interpolations (see below).

## Multiple Replacement Tokens in a Choice
It is possible to have multiple replacement tokens ('$') in a single choice. The choices for the first token must be separated from the choices for the second token by a '$' with the same level of indentation as the choices. (If you want to draw from the same pool for both, you can put your choices in a namespace, and then reference that before and after the '$' separator.

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
It is valid to have a replacement token with no text, and only a weight. This can be useful to, e.g., randomly choose between adding an extra clause onto a choice, or leaving it as is.

## Overriding Replacement Order
Normally, replacements are done starting from the first substitution symbol ('$') and proceeding from left to right. This can be overridden by using
substitution symbols of the form '\$\[\d+\]', to indicate which child you want to go into that substitution slot. If you override one symbol in a
given choice, you must override all of them. If you only override some of them, the outcome is undefined.

For example, if you wanted to reverse the substitution order of a choice, you could possibly do this:
```
10 Choice 3: $[3], Choice  2: $[2], Choice 1: $[1]
  10 Result 1
  $
  10 Result 2
  $
  10 Result 3
```

## State
Choices can write and read state. This can allow you to make choices more consistent. For example, picking expensive choices could increment a
'wealth' counter, which could make future expensive choices more likely. The symbol '%' is used for state manipulations.

### Writing State
State can be written by writing '$statename:$operation$value_modification', inside of a pair of '%'. State names are of the form '[a-zA-Z]\w+, allowed operations are '+=', '-=', '*=', '/=', '^=', and '=', and allowed value modifications are integers or other states. The exact format is
'%[a-zA-Z]\w+:[+=-/\*]"?[\w ]+"?%'.
* State writing operations must occur at the end of a line.
* The first '%' must be preceded by a space.
* Multiple state writing operations on one line are allowed.
* All states default to the value 0.
* The special token "@" is also allowed as an operation, and sets the specified state to the current choice value. It does not allow a
value modification to be provided, since the value modification is the current choice.

For example, a choice that writes '50' to the state 'wealth' would be:
```
125 Pile of Gold %wealth:=50%
```
And a choice that increases wealth by 25 (or sets it to 25, if it's unset) would be:
```
125 Pile of Gold %wealth:+=50%
```

### Using State
State can be used to modify random number generation or the probabilities of choices. To do this, put a state clause immediately after the
number you want to modify. These clauses are also placed inside of '%', and consist of an operation, followed by a value modification. In this case, the allowed value modifications are integers or other states. The exact format is '%([+=-/*])(\w+)%'. Using state to modify an element must
not have a space before the first '%'.

For example, using state to multiply the output of a random number by 10 would be:
```
50 My random number is [1-10]%*10%
```
And a choice that uses state to increase probability by the value of the 'wealth' state would be:
```
10%+wealth%
```

### Conditional State
State operations (writing, using, and interpolation) can be made conditional. This involves placing a condition, followed by a '->', before one of the state operations shown above. Conditions permit any boolean expression to be used in them.

For example, a conditional state that assigns the value 20 into the 'wealth' state if the 'nobility' state is equal to 'noble' would be:
```
25 King's grant %nobility=="noble"->wealth+20%
```
And a choice that would multiply its probability by the wealth value if the wealth value is not equal to 0 would be:
```
10%wealth!=0->*wealth% Treasure Chest
```

### Mathematical Expressions in State Manipulations
State operations allow for arbitrary mathematical expressions to be used on both sides of a comparison in a conditional state operation, and in the effect segment of any state operation. Inside a mathematical expression, expressions are evaluated with floating points, but will be converted to an integer by taking the floor before being used.

For example, the below expression will set the 'invitation' state to the value '"true"' if the sum of the value in the wealth state and ten times the value in the magic_items state is greater than 100 times the nobility level:
```
 10 some random choice %(wealth+magic_items*10)>nobility_level*100->invitation:="true"%
```

### Using Strings in State
Strings are allowed in states, but support fewer operations. They can be stored into states, read from them, compared for
equality/inequality, and concatenated.

For example, you could set the 'nobility' state to 'baron', and check against it later on, but there is no ability to see if a string is in a list, check if it's a substring of another string, or anything like that.

### String Expressions in State Manipulations
Strings can be concatenated in expressions with "+". This concatenation will work on other quoted strings, states, or the results
of a sub-expression. In the latter case, the result will be converted to an integer before being concatenated, if it is numeric.

### Interpolation
State values can be inserted into a choice by putting the state name, surrounded by percent signs, such as '%my_state%'. The state will then be replaced by whatever value is in that state when that clause is evaluated. (For more on evaluation order, see below.) If the state is not present when evaluated, the interpolation will be removed. If there is any choice text associated with the interpolation, you can surround it in a bracket clause, as detailed above, and the entire clause within the brackets will be removed if the value is not present.

### Conditional Interpolation
It's worth an explicit callout that you can apply conditionals to interpolated states, which will cause the entire surrounding bracket clause to be removed if the condition is false. This can be very useful, e.g., it allows you to adjust wording based on a value:
```
    10 I have {%children==0%->%no children}{%children>0->children% children}.
```

### Storing Tag Results
It's possible to store the results of a sub-choice into a state by appending a clause of the form '%state_name:@%' after the tag ("$").

### Silent Tags
You can make a call to a sub-choice without interpolating it into the main choice by surrounding the choice with curly braces. This
works for both the default form '{$}' and the order-overriden form '{$[1]}'.

### Execution Order
Execution occurs from left to right, evaluating each substitution token, subtable call, and random number generation as it is found,
before proceeding on.

If the order of substitution tokens is overridden, each token "owns" the text between itself and the next token,
and that owned text will be evaluated left-to-right for subtable calls and RNG before proceeding on to the next token.
The text before any tokens will be evaluated first, as if there was a virtual "0th token" at the start of the choice.

### Comments
Comments are indicated by a '#'. Nothing after the '#' will be processed, so make sure to use them at the end of a line!

## Examples
An example file, demonstrating many of these features, is present in test_places.txt. (Note that this test file also tests some code functions, specifically
constructing a namespace manually, so there is currently no file for @countries_table, as it is dynamically created.)
