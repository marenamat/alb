#!/usr/bin/perl

use warnings;
use Data::Dump;

print $ARGV[0], "\n";

my $TARGET = '<redacted>'

my %files;
opendir D, $ARGV[0] or die "opendir $ARGV[0] failed: $!";
map {
  m/^([^_]+)(_[^.]+)?\.[^.]+$/ or die $_;
  push @{$files{$1}}, $_;
} grep m/^[^.]/, grep m/(jpg|JPG|png|PNG)$/, readdir D;
closedir D;

mkdir "$ARGV[0]/views" or warn "mkdir: $!";

open M, ">", "$ARGV[0]/views/Makefile" or die $!;

print M <<EOM;
%.jpg:
\tconvert -scale 1024x1024 -quality 70% \$< \$@
EOM

my @k = sort keys %files;
#dd \@k;
for (my $i=0; $i < @k; $i++) {
  printf M "all: img%04d.jpg\n", $i;
  printf M "img%04d.jpg: ../%s\n", $i, (reverse sort @{$files{$k[$i]}})[0];
}

print M <<EOM;
install:
\trsync -avvzd . $TARGET/$ARGV[0]/
EOM

print M ".PHONY: all install\n";

close M;

chdir "$ARGV[0]/views";
shift @ARGV;
exec ("make", @ARGV);
