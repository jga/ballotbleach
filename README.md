************
ballotbleach
************

Data quality and analysis tools for surveys implementing the Civic Leadership Assessment specification.

## Getting Started

### Installation

**ballotbleach** is not on `pypi`, so if you want to use it, get the master onto your local machine
and create a distribution using Python 3. Then install into the virtual environment for the project that will
use **ballotbleach**.

### Command Line

You run **ballotbleach** from the command line. An `ini` configuration file is required.

The **ballotbleach** command takes an optional initial argument with the name of an action; it also
accepts values for `--cutoff`, `--conf`, and `--input` options.

ballotbleach [action] [--cutoff number] [--conf filepath] [--input filepath]

The default action value is "full".
The default `--cutoff` value is 75.
The default `--conf` value is *ballotbleach.ini*.
The default `--input` value is *raw-ballots.xlsx*.

### Configuration

The `ini` configuration file (*ballotbleach.ini* by default) has two sections: `[ballotbleach]`
and `[ballotbleach.charts]`. Below is a listing of the keys loaded by **ballotbleach** from the
configuration file.

#### [ballotbleach] section

**log_level**

This determines the logger level that will be printed on the console. **ballotbleach** logging is set to *INFO* as
the default.

**input_file**

The path to the file with the ballot input source data. If not set either in the `ini` file or through the
command line option, the application expects *raw-ballots.xlsx* in the directory **ballotbleach** is run from.

**output_directory**

As part of its work, **ballotbleach** writes out several files and creates chart images. By default, the application
expects there to be a *results* directory below the directory from which it the application is run. So, if the
application is run from `me/app`, then **ballotbleach** will write out data to `me/app/results` by default. You can
change the path by setting a different value for the `output_directory` key.

**risk_cutoff**

As part of the application, each submitted survey response (a 'ballot') is examined to determine if
the vote is genuine or if it's an attempt at ballot-stuffing. A risk score is assigned to each ballot. The cutoff
value is selected by the user to determine the score at which a ballot's risk points are too high and therefore
no longer deemed a genuine vote.  Ballots exceeding the cutoff are not included in the "clean" output CSV file;
they are also not considered for the analysis charts. The default cutoff is 75. Note, if you set the cutoff to 0,
all ballots will be rejected.

#### [ballotbleach.charts] section

**actor_ranking_title**

The text for the title of the bar chart generated by the application to rank the selected "actor" names.  By default, the title text on this chart
is *Most Selected*.

**actor_ranking_tick_format**

The x-axis tick format passed to the plotting library. The default is *%d%%*.

**actor_ranking_image_name**

The name given to the bar chart image of the actor ranking. The default name is *most-selected*, which the application
proceeds to save as *most-selected.png*. Don't include the file type in the name.

**subject_rating_title**

The text title for the bar chart plotting the distribution of ratings for the assessment subject. The default setting is
*Rating*.

**subject_rating_image_name**

The name given to the bar chart image of the subject rating. The default name is *rating*, which the application
proceeds to save as *rating.png*. Don't include the file type in the name.

**subject_rating_range**

A list (`[]`) of positive integers allowed as scores for the subject rating. The default is *1, 2, 3, 4, 5*. An example
setting:

```
    subject_rating_range=[1,2,3,4,5,6,7,8,9,10]
```

**mask_file**

The path for an image. This image will be used as a mask for the "word cloud" generated from feedback inputs.
There is no default.

**stop_words**

A list (i.e. `[]`) of words that the word cloud generator should skip. Example setting:

```
    stop_words=["alpha", "beta"]
```

Even if there is only one word, it must be in enclosed by list brackets as the value as parsed by
Python's `json` library. Words must be in quotations.

There is no default value for this option; however the `word_cloud` library that generates the image does have
a base list of stop words.

## Run Tests

Make sure `py.test` is installed. Then:

```
    $ py.test tests
```