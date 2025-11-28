# J2B
Wenatchee Seventh Day Adventist Church's Journey to Bethlehem Timekeeping Technology Systems

## System Overview
Journey to Bethlehem requires the actors to transition each group of journeyers along to the next part of their journey. The actors need to know when to do this, and keep the whole operation on a pretty rigid schedule. If things are out of sync, we’ll have too many groups in some areas, getting jumbled together, or not enough groups in the village, and we won’t be able to get through the number of groups we’d like to as fast as we would like to. There are a lot of people who want to experience Bethlehem, and getting everyone the opportunity is our goal.

In order to get all the groups through, a system for keeping everything synchronized and in time is necessary. In past years, this has been done with walkie-talkies given to specific actors called time-keepers in the village. Someone with a walkie-talkie would be watching a clock, and every 4 minutes or so, would say “30 30 30,” to let all the time-keepers in the village know that they had 30 seconds until the groups would need to move on, and “GO GO GO,” to let the time-keepers know it was time to move the groups to the next section of their journey. The advantages of this system were that, ideally, each time-keeper would be able to have an earpiece, and would be able to clearly hear the message. However, in practice, the walkie-talkie system was very spotty, and groups would end up out of sync.

In Christmas of 2024, we built a new system. Peter Kyle designed an automated system using little plastic candles, and audio cues in the village. These all connect to a controller that lives in the FLC. The controller can be started in automatic mode (or manual mode) to make the candles flicker out in time to let the time-keepers in the village get the message. One candle burns out at “30 30 30,” and the other candle then burns out at “GO GO GO.” After about 10 seconds, both candles come back to a flickering flame again.

<img width="956" height="650" alt="Controller" src="https://github.com/user-attachments/assets/8df7c5a0-12f7-4bcf-94be-f2206f531ece" />
<img width="912" height="888" alt="Candle" src="https://github.com/user-attachments/assets/a726991a-932e-4260-94cb-2117fecc82a1" />

With this new system, a web interface was also built. People can open their web browser on their phone or computer and navigate to the public-facing web interface to view the timekeeping clock. People responsible for calling groups and setting the current performer text on the projector screen can also use this web interface to do this.

<img width="611" height="1358" alt="Screenshot of Web Interface" src="https://github.com/user-attachments/assets/3bd39629-aa45-4265-a863-a607457ecf93" />

When a group get's called, it's important to get people's attention in the sanctuary. Putting up the big group number text on the screen is not quite enough to get people's attension if they aren't looking at it. To accomplish this, whenever a group is called, the program on the projection PC sends a GET request to the church Home Assistant server, which then is received by Node-RED, and triggers a Home Assistant script that brings the houselights and christmas lights up in brightness, and triggers an animation on the valance lights. After about 30 seconds, the houselights dim down again.

