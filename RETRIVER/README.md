# HYBRID BSGS + Kangaroo

A Pollard's kangaroo interval ECDLP solver for SECP256K1 (based on VanitySearch engine).\
**This program is limited to a 256 bits interval search.**

# Edits to change Options

Options has been added to start and end the KeySearch range in command line using -st and -en. Ex: -st 1 -en ffffffff
If -en is not given with -st then default 10000 Trillion keys are taken from start key.

Also a random startbit with a given range is added by using -rb and -seq. Ex: -rb 256 -seq ffffffff
If none of these 2 start options are given, then random start in 256 bit is taken as start key and 10000 Trillion as Range.

These -st,-en options are complementary to -rb,-seq. both can not be used together.
The idea is that input Pubkey file must have only public keys, nothing else.

# Running Status

