#!/bin/sh

# Eseguo i comandi per montare i path
[ -b $1 ] || mknod --mode 0600 $1 b $2
mkdir /tmpmnt
mount $1 /tmpmnt
mkdir -p $4
mount -o bind /tmpmnt/$3 $4
umount /tmpmnt
rmdir /tmpmnt






