# VPN-Jail

Isolate an application to just VPN access and prevent data leaks especially when the VPN is down.


This script creates a network namespace to run the VPN. The namespace has IP Table rules that block all traffic apart from to the VPN provider & local locations. This ensures that if the VPN ever goes down no unencrypted data will be sent out over the internet. It's very simple to use all you need is to have a OPENVPN client & an application you need to run (rtorrent, firefox or popcorn-time)


Usage
=====

<pre><code>sudo ./vpnJail.sh vpn.ovpn firefox </code></pre>
<pre><code>sudo ./vpnJail.sh config_path process </code></pre>

Installation
============
Requires OPENVPN
<pre><code>sudo apt-get install openvpn</code></pre>

<pre><code>git clone git@github.com:OtherOfIce/VPN-Jail.git </code></pre>


Thanks to Schnouki: For his brilliant post (https://schnouki.net/posts/2014/12/12/openvpn-for-a-single-application-on-linux/)
