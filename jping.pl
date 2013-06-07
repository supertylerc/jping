#!/usr/bin/perl

use Net::SSH::Perl;
use NetAddr::IP;
use Getopt::Std;
use Fcntl ':seek';
use File::HomeDir;
use warnings;
use strict;

main();

sub main {
    print "Tyler's Juniper Pinger\n";
    print "v0.7.2\n";
    print "Licensed under BSD 2-Clause License\n";

    my ($router, $options_ref, $stat) = &init();
    my @vpn_interfaces;
    my $heading_hash = '#' x 40;
    my $heading_space = ' ' x 10;
    if ($options_ref->{i}) {
        print "$heading_hash\n";
        print "#  $heading_space  $heading_space  $heading_space  #\n";
        print "#$heading_space Routing Instances$heading_space#\n";
        print "#  $heading_space  $heading_space  $heading_space  #\n";
        print "$heading_hash\n";
        &vpn_routes($router, \@vpn_interfaces, $options_ref, $stat);
        print "\n\n";
        print "$heading_hash\n";
        print "#  $heading_space  $heading_space  $heading_space  #\n";
        print "#$heading_space  Global  Routes  $heading_space#\n";
        print "#  $heading_space  $heading_space  $heading_space  #\n";
        print "$heading_hash\n";
        &inet0_routes($router, \@vpn_interfaces, $options_ref, $stat);
        #close $stat;
    } else {
        &recheck($router, $stat);
        close $stat;
        unlink ".$options_ref->{r}.init";
    }
}

sub init {
    my %options = ();
    my $router_ip;
    getopts("iphmr:", \%options);
    if (!$options{r}) {
        &help();
    } else {
        $router_ip = $options{r};
    }
    my $init_file = File::HomeDir->my_home . "/.$router_ip.init";
    my $stat;
    if ($options{i}) {
        open($stat, '>', $init_file) or die "Couldn't open: $!";
    } elsif ($options{p}) {
        open($stat, '<', $init_file) or die "Couldn''t open: $!";
    } else {
        &help();
    }

    open(my $settings, '<', 'creds') or die "Someone deleted the settings file! >:[\n";
    my ($user, $pass) = split(/::/, <$settings>);
    chomp($user);
    chomp($pass);

    print "Establishing connection to $router_ip...\n";
    my $router = Net::SSH::Perl->new($router_ip, protocol => 2);
    print "Logging into $router_ip...\n";
    $router->login($user, $pass);
    print "Successfully logged in...\n\n\n\n";

    return $router, \%options, $stat;
}

sub vpn_routes {
    my $router = shift;
    my $vpn_if = shift;
    my $options_ref = shift;
    my $stat = shift;
    my $cmd = 'show configuration routing-instances | display set | match interface';
    my @output = $router->cmd($cmd);
    my @vrf_config;
    if ($output[0]) {
        @vrf_config = split(/\n/, $output[0]);
    } else {
        print 'No routing instances configured.';
        return;
    }
    my @headings = qw(Interface VRF IP Pass/Fail);
    my $dashes = '-' x 70;
    printf "%-17s%-25s%-19s%-9s\n",
        $headings[0], $headings[1], $headings[2], $headings[3];
    print "$dashes\n";
    foreach (@vrf_config) {
        my @vrf_elements = split(/ /);
        my $vrf_name = $vrf_elements[2];
        if ($options_ref->{m}) {
            if ($vrf_name =~ m/IGNORED_VRFS_HERE/) {
                next;
            }
        }
        my $vrf_interface = $vrf_elements[4];
        push(@$vpn_if, $vrf_interface);
        $cmd = "show configuration interfaces $vrf_interface family inet | display set | match address";
        @output = $router->cmd($cmd);
        if (!$output[0]) {
            next;
        }
        my @ip_config = split(/\n/, $output[0]);
        my @check_for_dups;
        my $ip_cidr;
        foreach (@ip_config) {
            my @ip_elements = split(/ /);
            $ip_cidr = $ip_elements[8];
            if (grep /$ip_cidr/, @check_for_dups) {
                next;
            }
        }
        push(@check_for_dups, $ip_cidr);
        foreach (@check_for_dups) {
            if (!$_) {
                next;
            }
            my @cidr = split(/ /);
            my $ip_block = NetAddr::IP->new(@cidr);
            for my $ip (@{$ip_block->hostenumref}) {
                my $addy;
                if ($ip_cidr !~ m/\/31/) {
                    $addy = $ip->addr;
                } else {
                    print "This is a slash 31.\n";
                    $addy = $ip->nth(0);
                    $ip_cidr =~ s/\/.*//;
                    if ($ip_cidr eq $addy) {
                        $addy = $ip->nth(1);
                    }
                }
                $ip_cidr =~ s/\/.*//;
                if ($ip_cidr eq $addy) {
                    next;
                }
                $cmd = "ping routing-instance $vrf_name $addy rapid count 2";
                @output = $router->cmd($cmd);
                my @ping = split(/\n/, $output[0]);
                if ($ping[1] ne '..') {
                    printf "%-17s%-25s%-19s%-9s\n",
                        $vrf_interface, $vrf_name, $addy, $ping[1];
                    print {$stat} "$addy,$vrf_name,$ping[1],$vrf_interface\n";
                }
            }
        }
    }
}

sub inet0_routes {
    my $router = shift;
    my $vpn_if = shift;
    my $options_ref = shift;
    my $stat = shift;
    my $cmd = 'show configuration interfaces | display set | match "family inet address"';
    my @output = $router->cmd($cmd);
    my @intf_config = split(/\n/, $output[0]);
    my @headings = qw(Interface IP Pass/Fail);
    my $dashes = '-' x 47;
    printf "%-17s %-19s %-9s\n", $headings[0], $headings[1], $headings[2];
    print "$dashes\n";
    my @check_for_dups;
    foreach (@intf_config) {
        my @intf_elements = split(/ /);
        my $interface = "$intf_elements[2].$intf_elements[4]";
        $cmd = "show interfaces terse $interface | match $interface";
        @output = $router->cmd($cmd);
        my @intf_state = split(/ +/, $output[0]);
        if ($intf_state[2] =~ m/down/) {
            next;
        }
        my $ip_cidr = $intf_elements[8];
        if (grep /$interface/, @$vpn_if) {
            next;
        }
        if (grep /$ip_cidr/, @check_for_dups) {
            next;
        }
        push(@check_for_dups, $ip_cidr);
        my $ip_block = NetAddr::IP->new($ip_cidr);
        my $p2p_addy;
        if ($ip_cidr =~ m/\/31/) {
            $ip_cidr =~ s/\/.*//;
            $p2p_addy = $ip_block->nth(0);
            if ($ip_cidr eq $p2p_addy) {
                $p2p_addy = $ip_block->nth(1);
            }
            $p2p_addy =~ s/\/.*//;
            $cmd = "ping $p2p_addy rapid count 2";
            @output = $router->cmd($cmd);
            my @ping = split(/\n/, $output[0]);
            if ($ping[1] ne '..') {
                printf "%-17s %-19s %-9s\n", $interface, $p2p_addy, $ping[1];
            }
        } else {
            for my $ip (@{$ip_block->hostenumref}) {
                my $addy = $ip->addr;
                $ip_cidr =~ s/\/.*//;
                if ($ip_cidr eq $addy) {
                    next;
                }
                $cmd = "ping $addy rapid count 2";
                @output = $router->cmd($cmd);
                my @ping = split(/\n/, $output[0]);
                if ($ping[1] ne '..') {
                    printf "%-17s %-19s %-9s\n", $interface, $addy, $ping[1];
                    print {$stat} "$addy,inet0,$ping[1],$interface\n";
                }
            }
        }
    }
}

sub recheck {
    my $router = shift;
    my $stat = shift;

    my @headings = qw(Interface VRF IP Pass/Fail);
    my $dashes = '-' x 70;
    printf "%-17s%-25s%-19s%-9s\n",
        $headings[0], $headings[1], $headings[2], $headings[3];
    print "$dashes\n";

    while (<$stat>) {
        my @check = split(/,/);
        chomp(@check);
        my $addy = $check[0];
        my $vrf_name = $check[1];
        my $success = $check[2];
        my $interface = $check[3];
        my $cmd;
        if ($vrf_name eq 'inet0') {
            $cmd = "ping $addy rapid count 2";
        } else {
            $cmd = "ping routing-instance $vrf_name $addy rapid count 2";
        }
        my @output = $router->cmd($cmd);
        my @ping = split(/\n/, $output[0]);
        if ($ping[1] !~ /!/) {
            printf "%-17s%-25s%-19s%-9s\n",
                $interface, $vrf_name, $addy, $ping[1];
        }
    }
}

sub help {
    print "HALP!";
    exit;
}
