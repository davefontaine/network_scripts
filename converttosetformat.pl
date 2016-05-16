#!/usr/bin/perl

#-----
# This script converts juniper configs to 'set' format for easier parsing by 
# other scripts.
#-----

@configfiles = @ARGV;

foreach $file (@configfiles) {
  chomp $file ;
  $file =~ s/.*\/// ;
  undef @setstring ;
  print "processing: ", $file, "\n";
  #next;

  open(CONFIG, "<$file") ;
  open(OUTPUT, ">$file.set") ;
  
  while(<CONFIG>) {
    $currentline = $_ ;
    chomp $currentline ;
    
#----- This part matches the very beginning of a long phrase
#----- Example: groups {
#----- We will start a phrase/string with a PUSH command
#----- Further complicating things is that sometimes there are comments in the config that might look like 
#----- 		input { ## Warning: 'input' is deprecated
    if ($currentline =~ m/^[a-z,A-Z]/ && $currentline =~ m/ {/) {
      $currentline =~ s/ {.*$// ;
      push(@setstring, $currentline) ;
    }

#----- This part maches the end of a long phrase
#----- Example: 		next-hop 1.2.3.4;
#----- Since this is the end of a 'set' style phrase/string, we'll print our completed string and then trim the last thing off the end. (Shorten the string one level)
    if (($currentline =~ m/\;$/ || $currentline =~ m/\; ## SECRET-DATA$/ ) && $currentline !~ m/^[a-z,A-Z]/) {
      $currentline =~ s/^\s+// ;
      $currentline =~ s/\;$// ;
      push(@setstring, "$currentline") ;
      print OUTPUT "set @setstring\n" ;
      pop(@setstring) ;
    }

    if ($currentline =~ m/ {/ && $currentline !~ m/\s*\#/) {
      $currentline =~ s/^\s+// ;
      $currentline =~ s/ {.*$// ;
      push(@setstring, "$currentline") ;
    } 

    if ($currentline =~ m/\s+}/ || $currentline =~ m/^}$/) {
      pop(@setstring) ;
    } 

  }

  close(CONFIG) ;
  close(OUTPUT) ;

}
