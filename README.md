# VPN-Jail

Isolate an application to just the VPN access and prevent data leaks & breaches especially when the VPN is down.


This script creates a network namespace to run the VPN. The namespace has IP rules that block all traffic apart from to the VPN provider. This ensures that if the VPN ever goes down no unencrypted data will be sent out. It also helps protect your own network from breaches.

Requires OPENVPN

Usage
=====

<pre><code>sudo ./vpnJail.sh vpn.ovpn firefox </code></pre>
<pre><code>sudo ./vpnJail.sh config_path process </code></pre>

Installation
============

<pre<code>git clone git@github.com:OtherOfIce/VPN-Jail.git </code></pre>


Thanks to Schnouki: For his brilliant post (https://schnouki.net/posts/2014/12/12/openvpn-for-a-single-application-on-linux/)
