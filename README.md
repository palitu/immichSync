# immichSync

This quick script was put together so that i could use immich to build photo galleries, with descriptions, and be able to synchronise them to my family blog.  Currently i manually create the post and gallery, selecting the photos that were last uploaded.

Features:
 - [x] Select from the list of all immich albums.
 - [x] Synchronise photo from Immich to Wordpress.
 - [ ] Retry failed uploads & downloads
 - [x] de-duplication of Immich photo uploads (multiple uploads if the file exists in multiple albums)
 - [x] Set the photos "Caption".  Description and Alt-text are easy to add, but there is no equivalent in Immich.
 - [x] Track state of upload and mapping between resources in Immich and Wordpress
 - [ ] Update meta-data in Wordpress if it changes in Immich.
 - [ ] Automatically create a new WP post for each selected album
 - [ ] Populate the Immich album descriptin in the WP 'album post'
 - [ ] Automatically populate WP 'album posts' with all photo from the Immich album

I expect that i will slowly add features if i get the motivation, but i would wlecome a PR.  I am having issues with the WP Posts, but i imagine that it due to some of my 'forced auth' plugins that i am using.

# Contributing
If you would like to contribute, i am happy to review.  Maybe stick a comment into the issues firsts.  Also note that i am a novice programmer (as you can see :D), so my ability to determine good quality code is limited, apart from seeing that my code is sunny-day, and has limited/no error handling.
