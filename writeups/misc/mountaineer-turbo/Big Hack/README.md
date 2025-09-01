

We’re supposed to find the name of the town which is 300 meters away from where this photograph was taken.

![[mountaineer.webp]]

Ah, it’s beautiful. A dense green forest, a river and a tall mountain. This looks great, it must be Norway!
The challenge description says the mountain is 3060 meters tall! Wow, well, how many mountains in Norway are over 3000 meters tall? A quick google search revealed this:
### **None**

… oh, well. Great! My ego is bruised, but I’m one step closer to finding the flag! Now, if there are no 3000 meters tall mountains in Norway, where are they?! Someone must have made a LIST and put it on the internet! I’ve spoken to enough geologists to feel pretty confident about this. 

A quick google search led me here: https://en.wikipedia.org/wiki/List_of_prominent_mountains_of_the_Alps_above_3000_m

What a title → “List of prominent mountains of the Alps above 3000 m” - it’s like music to my ears. A quick ctrl/cmd+f of 3060 takes me to the humble entries of 478, and 479.

![[Pasted image 20250901152023.webp]]

Seeing as both “Piz Grisch” and “Grand Queyron” have dedicated wikipedia articles, I may as well check ‘em out while I’m here. 

Let’s have a look at Piz Grisch:
![[Pasted image 20250901153218.webp|700]]

Enhance
![[Pasted image 20250901153252.webp|528]]

Enhance
![[Pasted image 20250901153337.webp|527]]

Enhance again
![[strangeMonkeyOnMountain-1.webp]]

Woah, what’s that? If my eyes don’t deceive me, there seems to be a monkey sitting on top of that mountain. And it’s typing on a keyboard? Well, this is most strange, but I don’t see how it’s relevant to solving this challenge. Perhaps this is what some refer to as a “red herring”.

Now let’s look at our original picture
![[mountaineer.webp]]
Wow so pretty :)

Let’s have a closer look:
![[Pasted image 20250901160906.webp]]

Side by side:
Original image vs Piz Grisch Wikipedia image
![[Pasted image 20250901161915.webp]]

I put in the extra effort to reveal my image comparison algorithm, which involves looking at the image, with my eyes… I drew a line to visualize what pattern I see during such a process. I’m noticing that the shape on the top of the mountain looks pretty similar.

Now I think I’m ready to search for the town that is 300 meters away from the location of the photograph. For this I am using Google Maps and locating the Piz Grisch mountain on the map.

![[Pasted image 20250901153132.webp]]

Here there are two close by towns, Ferrera and Ausserferrera. From the challenge description we know that the photo was taken approximately 3700 meters away from that mountain. Since we only have two towns close by, I’m going to use the handy “Measure distance tool” that Google Maps provides (pretty nifty!)

![[Pasted image 20250901163856.webp]]

First, let’s check Ferrera
![[Pasted image 20250901164144.webp]]
2.44 km - that’s 2440 meters, over 1000 meters off from the 3700 meter distance we’re looking for.

How about Ausserferrera
![[Pasted image 20250901164350.webp]]
3.70 km, that’s 3700 meters! Exactly what we’re looking for!!!

At this point I’d try entering Ausserferrera as the flag, but I’m not in a rush, so let’s check out Ausserferrera on street view and see if it resembles our original photo.
![[Pasted image 20250901171745.webp]]
Well, it’s as bright as the lord, but I’m pretty sure that’s the same nipple formation I saw earlier.

The flag format in the description says: Flag: NNS{name_of_town}
→ Locking in NNS{Ausserferrera}
and BOOM! … WRONG! What?!
Let’s try again, maybe the a is lowercase?
→ Locking in NNS{ausserferrera}
and SUCCESS! <span style="color:green">You have solved this challenge! 🎉🎉 </span>

-----
DISCLAIMER: I actually checked out many different mountains before figuring out it was this Piz Grisch, and I must come clean, I didn’t even use the measuring tool! I thought of that during this writeup! I’ll definitely use it in future challenges though, it’s pretty useful. Instead I checked the street view of both towns, I even checked street view in the bordering country of ITALY 🤦‍♂️… It IS visible from Italy though! From the south side… ![[Pasted image 20250901170902.webp]]