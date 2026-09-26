package HarmonyCwd;
use strict;
use warnings;
use Cwd ();

# Scoped to the bundled latexmk process. Preserve native behavior whenever it
# succeeds. Never trust an inherited logical path without comparing directory
# identity, and never substitute it for abs_path/realpath of arbitrary files.
sub checked_pwd {
    my $path = $ENV{PWD};
    return undef unless defined($path) && $path =~ m{\A/} && index($path,"\0") < 0;
    my @here = stat('.');
    my @there = stat($path);
    return undef unless @here && @there && -d _;
    return undef unless $here[0] == $there[0] && $here[1] == $there[1];
    return $path;
}

my $native_getcwd = \&Cwd::getcwd;
for my $name (qw(cwd getcwd fastcwd fastgetcwd)) {
    no strict 'refs';
    # fastcwd's Perl fallback walks ancestors and can fail before restoring cwd
    # in an OHOS sandbox. Use the non-mutating native getcwd for these aliases.
    my $native = $name =~ /^fast/ ? $native_getcwd : \&{"Cwd::$name"};
    no warnings 'redefine';
    *{"Cwd::$name"} = sub {
        my $value = $native->(@_);
        return $value if defined($value) && length($value);
        return checked_pwd();
    };
}
1;
