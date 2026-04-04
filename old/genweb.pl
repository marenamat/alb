#!/usr/bin/perl

use warnings;
use Data::Dump;

print $ARGV[0], "\n";

system (qw/perl genviews.pl/, @ARGV);

opendir D, "$ARGV[0]/views" or die "opendir $ARGV[0]/views failed: $!";
my @files = sort grep m/^[^.]/, grep m/jpg$/, readdir D;
my $pos = 0;
closedir D;

open F, "<", "$ARGV[0]/index.md" or die "open $ARGV[0]/index.md: $!";
open P, "|-", "pandoc --template=genweb-template.html -f markdown -t html5 -i - -o $ARGV[0]/views/index.html -M og-prefix=https://alb.jmq.cz/$ARGV[0]/" or die $!;

while (<F>) {
  m/^!!(!)?$/ or print P $_ and next;
  my %state = ();
  unless (defined $1) {
    while (<F>) {
      m/^!!$/ and last;
      m/^!([a-z]+) +(.*)$/ and $state{_last} = $1 and $state{$1} .= " $2" and next;
      m/^!\s+(.*)$/ and (exists $state{_last} and $state{$state{_last}} .= " $1" or die "No last lang!") and next;

      die "Photo not ended!";
    }
  }

  my @langs = grep { ! m/^_/ } keys %state;

  print P "\n";
  print P "<img id=\"img-$pos\"";
  print P " data-prev=\"img-", ($pos-1), "\"" if $pos > 0;
  print P " data-next=\"img-", ($pos+1), "\"" if $pos+1 < @files;
  print P " data-langs=\"", (join ",", @langs), "\"";
  foreach my $lang (@langs) {
    print P " data-title$lang=\"$state{$lang}\"";
  }
  print P " class=\"img-tiles\"";
  print P " src=\"", $files[$pos], "\">\n";
  print P "<script>document.getElementById(\"img-$pos\").addEventListener(\"click\", showfoto)</script>\n";
  $pos++;
  print P "\n";
}

if ($pos < @files) {
  print P "\n\nTrailing images (", (scalar @files) - $pos, " of ", (scalar @files), ")\n\n";
  for ( ; $pos < @files; $pos++) {
    print P "<img id=\"img-$pos\"";
    print P " data-prev=\"img-", ($pos-1), "\"" if $pos > 0;
    print P " data-next=\"img-", ($pos+1), "\"" if $pos+1 < @files;
    print P " data-langs=\"\"";
    print P " class=\"img-tiles\"";
    print P " src=\"", $files[$pos], "\">\n";
    print P "<script>document.getElementById(\"img-$pos\").addEventListener(\"click\", showfoto)</script>\n";
  }
}

close P;
close F;

print "xdg-open file://" . `readlink -f $ARGV[0]/views/index.html`;
