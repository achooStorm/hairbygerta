# Moving hairbygerta.com off Wix: a step by step guide

This guide is for Gerta, the owner of Hair & Makeup by Gerta, and for whoever helps her. It shows how the salon website moves from Wix to the new site in the folder `hairbygerta`: what can be done now, what to check and save first, how the move itself goes, and what it costs afterwards.

Three things to know before you start:

- **The Wix site stays untouched.** Nothing in Sections 1 and 2 changes it. It keeps running exactly as it is until you decide to move the domain (the web address hairbygerta.com) in Section 3.
- **You can look at the new site in the meantime.** On the computer today, and on the internet at the preview address https://achoostorm.github.io/hairbygerta/ once the new site is published. Section 1, Part 1 shows both.
- **The photos are the one difference.** 26 photos of the Wix site cannot move to the new site. Section 8, Part 4 says why. On the new site a placeholder (a beige box with a faint logo) stands in for each of them until you put in a photo of your own. Never save, copy or upload a photo from the Wix site.

How to read this guide:

- **Your helper** is the person who built the new site and helps you with the computer steps.
- A step that starts with **Gerta signs in** happens inside one of Gerta's own accounts or her email. Gerta does it herself, or her helper does it with Gerta next to them, saying yes to each step. Nobody signs in as Gerta, asks for her passwords or codes, or types in her bank or card details for her. The same rule holds for every other step inside her Wix, Cloudflare, Square and email accounts.
- **The GitHub account** that holds the new site is called achooStorm. It belongs to your helper, not to Gerta. So every GitHub step in this guide is one where **your helper signs in**: publishing the site (Section 1, Part 5), setting the domain there (Section 4), publishing a photo (Section 6) and pasting the booking link (Section 7). Gerta cannot do those steps alone. The helper signs in with their own password and sign-in codes, and nobody else types them. What this means for the address hairbygerta.com, and which decision there is Gerta's, is in [Section 4](#whose-github-account-this-is-and-what-gerta-decides).
- **Bold words** in the steps are the names of buttons, menus and pages, written the way the official help pages write them.
- A marker like [S12] points to the list [Official help pages used](#official-help-pages-used) at the end. Every statement about how Wix, Cloudflare, GitHub or Square works comes from one of those pages. All of them were opened on 12 or 13 October 2026.
- Rules, prices and screens change. If a screen does not match a step, stop. Open the help page behind the marker, or ask your helper.
- Dates are written with the month as a word, for example 27 November 2026, so the day and the month cannot be mixed up.

## At a glance

Tick each step when it is done. The order matters. The link in each step leads to the part of this guide that explains it.

**Now, while everything stays on Wix**

1. [ ] This week: write down the three end dates in Wix, for the site plan, the domain and the business email. See [Section 2, Parts A to C](#2-what-to-check-in-wix-this-week). The domain date is the urgent one.
2. [ ] This week: back up the mailbox info@hairbygerta.com. See [Section 2, Part D](#part-d-back-up-the-mailbox).
3. [ ] This week: read [Section 8, What cannot be undone](#8-what-cannot-be-undone) once, before you change anything. It also says by when the Wix site plan and the business email have to be canceled if you do not want Wix to renew them.
4. [ ] Before the domain's payment date in Wix: decide with your helper how the domain will move and whether Wix should renew it one more time. See [Read this first](#read-this-first-it-takes-two-moves-not-one) and [Check your dates first](#check-your-dates-first) in Section 3. That part also says why the payment date may be as early as around 27 October 2026.
5. [ ] Look at the new site on the computer. See [Section 1, Part 1](#part-1-look-at-the-new-site).
6. [ ] Set up Square on the free plan and test a booking. See [Section 1, Part 3](#part-3-set-up-square-appointments-on-the-free-plan) and [Part 4](#part-4-test-a-booking).
7. [ ] Collect your own photos. See [Section 1, Part 2](#part-2-collect-your-own-photos).
8. [ ] Your helper publishes the new site, so that it opens at the preview address. Only the helper can do this, because the GitHub account is theirs. See [Section 1, Part 5](#part-5-your-helper-publishes-the-new-site-the-first-time).
9. [ ] Put your own photos in place of the placeholders, one at a time. See [Section 6](#6-how-to-replace-a-placeholder-with-a-real-photo). You can keep doing this after the move too.
10. [ ] Paste the Square booking link into the new site. See [Section 7](#7-how-to-paste-the-square-booking-link).

**The move: from here on the address hairbygerta.com changes hands**

11. [ ] Get Cloudflare ready. Cloudflare is the company that will hold the domain's settings. See [Section 3, Part A](#part-a-get-cloudflare-ready).
12. [ ] Make the first move of the domain. Start at least 2 to 3 weeks before the earliest end date you wrote down in step 1. See [Section 3, Part B](#part-b-first-move-from-wix-to-the-in-between-registrar).
13. [ ] Straight after the first move: point the domain at the new site, together with your helper. See [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages). Before that day, Gerta decides whether the domain is also locked to the helper's GitHub account: see [Whose GitHub account this is, and what Gerta decides](#whose-github-account-this-is-and-what-gerta-decides).
14. [ ] Turn on the free email forwarding, before the business email end date. See [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail). Then back up the mailbox one last time ([Section 2, Part D](#part-d-back-up-the-mailbox)).
15. [ ] Wait 60 days, then make the second move, into Cloudflare Registrar. See [Section 3, Part C](#part-c-wait-60-days) and [Part D](#part-d-second-move-into-cloudflare-registrar).

**Afterwards**

16. [ ] Before each of the three Wix payment dates and end dates: read the matching part of [Section 8](#8-what-cannot-be-undone) again. A payment date can come weeks before its end date, and Section 8 says how many. Do not cancel or close anything at Wix before you have read that part.
17. [ ] Once a year: check what you pay. See [Section 9](#9-yearly-cost-after-the-move).

Steps 11 to 15 follow the route with two moves. If you and your helper choose another way in step 4, for example to leave the domain registered at Wix, those steps change. Section 3 names the choices under [Read this first](#read-this-first-it-takes-two-moves-not-one).

## 1. What can be done now without touching Wix

Nothing in this section changes the Wix site, the domain or your email. Do Part 1 before Part 2, and Part 3 before Part 4. Parts 1 and 2 do not depend on Parts 3 and 4, so either pair can come first. Part 5 is for your helper and can be done on any day.

### Part 1: Look at the new site

**On the internet, once the site is published.** Your helper publishes the site. [Part 5](#part-5-your-helper-publishes-the-new-site-the-first-time) shows how. After it, the new site is at this preview address (a temporary web address, used until hairbygerta.com points to the new site):

https://achoostorm.github.io/hairbygerta/

GitHub is the service that will hold the site, on its free plan [S1] [S2]. It gives a site like this the address `https://<account name>.github.io/<site name>` [S1]. Anyone who has the address can open it [S3]. A published change can take up to 10 minutes to show [S3]. If the address does not open, the site is not published yet.

**On the computer, today.** This needs Python, a free program that is already on the computer where the site was built.

1. Open the folder `hairbygerta` in File Explorer.
2. Click the empty part of the address bar at the top of the window.
3. Type `cmd` and press Enter. A black window opens (Command Prompt, a window where you type commands).
4. Type `python -m http.server 8000 --bind 127.0.0.1` and press Enter.
5. Open your web browser and go to `http://localhost:8000` (localhost means "this computer", so nobody else can see it).
6. Click through every page.
7. Close the black window when you are done. This stops the preview.

The beige boxes with a faint logo are placeholders (stand-in pictures). Each one marks a spot for one of your own photos.

### Part 2: Collect your own photos

26 of the photos on the old site cannot move with you. Shutterstock photos bought through Wix may only be used on Wix and cannot be downloaded [S4]. The free Wix photos, and the photos that came with the Wix template, are for use within Wix only [S5].

A photo is safe to use only if one of these is true:

- You took it yourself.
- Someone else took it and you have their written permission to use it on your website. Keep the email or message.
- It is a stock photo you bought yourself outside Wix, and you still have the license that allows website use. Wix itself says to check which license you bought [S6].

Not safe: a photo saved or screenshotted from the old Wix site, anything in the folder `hairbygerta-wix-only-photos`, and photos found on Google, Pinterest or Instagram. If a client can be recognised in a photo, get the client's written OK too.

1. Start the preview on the computer (Part 1).
2. Right-click a beige box and choose **Open image in new tab**. The end of the address shows the placeholder's file name, for example `home-smile.jpg`.
3. Pick your own photo for that spot. Keep tall spots tall and wide spots wide. Most spots crop the photo to fit, so keep the hair or face near the middle.
4. Copy the photo you picked into a new folder of its own, for example a folder called salon-photos in your Pictures. Use the original photo file, not a screenshot. Do not put it into the `hairbygerta` folder yet.
5. Write down the placeholder's file name for this photo, and a few words on what the photo shows.
6. Repeat steps 2 to 5 for the next spot.

When a photo is ready to go onto the site, follow [Section 6](#6-how-to-replace-a-placeholder-with-a-real-photo). It shows how to save the photo in the right size and under the right name, and how to publish it. Section 6 also has a table of all 26 placeholder names. If those computer steps are not for you, give your helper the folder with your photos and your notes.

There are 26 placeholder names. You do not need all of them at once. A spot you do not fill stays a beige box. Some photos are used on more than one page.

**The logo.** The logo file is only 225 px wide and 225 px tall (px means pixels, the dots a picture is made of), so it can look a little soft on sharp screens. Ask whoever designed the logo for the original artwork (a vector file such as SVG, AI, EPS or PDF, or a large PNG). A sharper logo can then be put in later. Nothing has to change now.

### Part 3: Set up Square Appointments on the free plan

Square is the booking service the new site will link to. Its free plan is called Square Free. It costs \$0 a month per location (a location is one place of business, and you have one) and includes an online booking site [S7]. Square lists its card processing fees on the same page [S7]. What the free plan includes, and the fees, are in [Section 9](#square-free-plan-fees-only-on-payments). Square Dashboard is the Square website where you manage your account.

**Create the account**

1. Go to https://squareup.com/us/en/appointments/pricing
2. Under **Square Free**, click **Get started** [S7]. Do not click **Try free for 30 days**. That button starts a trial of a paid plan: Square Plus is \$49 and Square Premium is \$149 a month per location [S7].
3. Answer the sign-up questions yourself. For the login email, use an address you are sure will keep working while the website moves. A personal address is safer for this than info@hairbygerta.com.
4. If Square asks what kind of business you have, pick the choice closest to a hair salon. Square switches features on by business type [S8].
5. Verify your identity and link your bank account when Square asks. Square's setup guide lists this as its first step and says you need your bank account and routing numbers [S9]. Do this yourself. Do not give these numbers to anyone who helps you.

**Check your location**

6. In Square Dashboard go to **Account & Settings**, then **My business**, then **Locations** [S10].
7. Select your location. Square made it when you signed up [S10].
8. Check the business name (Hair & Makeup by Gerta), the address (Le Vigne Hair Salon, 644 Forest Ave, Staten Island, NY 10310), the phone (347-671-5095) and the email (info@hairbygerta.com).
9. Enter the business hours: Tuesday - Saturday, 9 AM - 5 PM.
10. Click **Save** [S10].

Before you go on, know this. If a menu, page or tab named in steps 11 to 25 is missing, the booking features are most likely not switched on yet. That can be **Service library** in step 11, the **Appointments** tab in step 19 or **Appointments** in step 25. Square does not show these features in Square Dashboard until they are activated [S11]. To activate them, go to **Add more** in Square Dashboard, select **Bookings** and click **Add** [S11]. Square says some of these features need a paid plan [S11]. If a screen shows a price or asks you to change your plan, stop and ask your helper.

**Add the ten services**

11. Go to **Items & services**, then **Items**, then **Service library**. The first menu may be called **Items & menus** or **Items & inventory** [S12].
12. Click **Create service** [S12].
13. Type the name and the description from the table below.
14. Select the price type and enter the price [S12]. Read the note under the table first.
15. Enter the duration [S12].
16. Click **Save** [S12].
17. Repeat steps 12 to 16 for the other nine services.

| Name | Description | Duration |
|---|---|---|
| Haircut & Style | Transform your hair with precision cutting and styling. | 45 min |
| Hair Coloring | Revitalize your hair with our expert coloring services. | 1 hr 30 min |
| Makeup Session | Natural makeup that enhances your beauty. | 45 min |
| Dream Bridal Hair | Romantic, long-lasting bridal hair tailored to your dress and vision. | 1 hr 30 min |
| Highlights & Lowlights | Customized foils to add brightness, depth, and dimension. | 2 hr 30 min |
| Balayage | Hand-painted color for a soft, sun-kissed finish. | 3 hr |
| Keratin Treatment | Frizz-fighting smoothing treatment for sleek, manageable hair. | 2 hr 30 min |
| Brazilian Blowout | Long-lasting smoothness with mirror-like shine. | 2 hr |
| Perm & Texture Waves | Custom curls or waves with movement and body. | 1 hr |
| Kids’ Haircut | Friendly, patient cuts just for kids. | 45 min |

Note on price: your website says "Call for price" for every service. Square's help page does not name its price types, so this guide cannot tell you which one to pick. Open the price type list and read the choices. Pick the one that shows no fixed amount. If Square will not save without an amount, enter your real price. Never enter a guess.

**Make yourself bookable**

18. Go to **Staff**, then **Team**, then **Team members**. The first menu may be called **Staff & payroll** [S13].
19. Select your own name, then select **Appointments** [S13]. If your name is not in the list, stop and ask Square support (see the end of Part 4).
20. Select **Add to appointments** [S13].
21. Turn on **Bookable by customers online** [S12].
22. Choose all ten services as the services you offer [S12] [S13].
23. Set your hours of availability to Tuesday - Saturday, 9 AM - 5 PM [S13].
24. If the page shows a **Done** or **Save** button, click it.

To change your hours later, go to **Appointments**, then **Calendar**, click the clock icon in the top right corner and select **Recurring schedule** [S14].

**Turn on online booking**

25. Click **Appointments**, or **Payments** then **Appointments** [S15]. If you cannot find it, the booking features are not switched on yet [S15]. Add them as described in the note before step 11.
26. Click **Online Booking**, then **Channels** [S15].
27. Toggle ON **Enable online booking** (a toggle is an on/off switch) [S15].
28. Under **Booking channels**, click **Preview & edit** next to **Square Online website** [S15].
29. Use the options to create your online booking site. Square says this site is free [S15].
30. Click **Publish** in the top right corner [S15].
31. On the **Site published** page, copy your online booking site URL (URL means web address) [S15]. Paste it into a note.
32. Go back to **Online Booking**, then **Channels** [S15].
33. Under **Add your booking flow to an existing site**, click **Get Started** [S15].
34. Click **Get URL** [S15]. Do not use **Create button** or **Get embed code**. They give code, not a link [S15].
35. If Square asks for a location, select the salon [S15].
36. Select your booking type [S15]. Square's help page does not list the choices. You offer appointments for salon services. If you are not sure which choice fits, stop and ask your helper.
37. Copy the booking flow URL into the same note [S15].
38. Click **X**, then **Done** [S15].

Keep both links. Square means the booking flow URL to be used on another website [S15]. In this guide it is called your booking link. It goes behind the Book Now buttons of the new site in [Section 7](#7-how-to-paste-the-square-booking-link). Until then those buttons call 347-671-5095. Leave the Wix site as it is.

### Part 4: Test a booking

1. On your phone, open the online booking site URL from your note. You now see what a client sees.
2. Check that all ten services are there, with the right names, descriptions and durations. Look at how the price shows.
3. Choose a service.
4. Check that the times offered are all within Tuesday - Saturday, 9 AM - 5 PM.
5. Book a time with your own name, email and phone number.
6. Write down which messages you get as the client. Square says some notifications need specific subscriptions or settings [S16]. The settings are under **Appointments**, then **Settings**, then **Communications** [S17].
7. On the computer, in Square Dashboard, go to **Appointments**, then **Calendar** [S14]. Bookings made on the booking site go to your calendar [S15], so the test booking should be there.
8. If it shows as pending, select it and click **Accept**. Select a notification type, email or text, add a message if you like, and click **Send** [S18]. Whether bookings are accepted automatically is the **Reservation Guarantee** setting under **Appointments**, then **Settings**, then **Calendar & booking** [S17].
9. Now cancel the test. Go to **Appointments** (or **Payments** then **Appointments**), then **Settings**, then **History**, and select the test appointment [S17]. Square's help page files this list under past appointments [S17]. If the test is not listed there, go back to **Appointments**, then **Calendar**, and click the appointment there instead [S14].
10. On the **Appointment Details** page click **More**, then **Cancel Appointment** [S17]. If you see no **More** button, stop and ask Square support.
11. Choose how to notify the client and confirm [S17].
12. Open your booking link from your note and check that it also opens your booking page.

If something is wrong, fix it in Part 3 and test again. If a screen does not match these steps, Square has changed it since 13 October 2026. Open the help page for that step from the list at the end of this guide, or ask Square support. Square's customer support number is 1 (855) 700-6000 [S7]. On Square Free, Square lists phone support as 6am to 6pm Pacific time, Monday to Friday, and only for the first 90 days [S7]. It lists chat support and email support for Square Free without such a limit [S7].

### Part 5: Your helper publishes the new site the first time

This part is for your helper. The GitHub account achooStorm is the helper's own, so the helper signs in and Gerta cannot do this part alone. It changes nothing at Wix and nothing about the address hairbygerta.com. It needs the folder `hairbygerta`, Python and Git (the free program that sends files to GitHub) on the helper's computer.

Know this before you start: with the free GitHub plan the repository (the project on GitHub that holds the site files [S63]) must be public, and the site itself is open to everyone on the internet [S3]. Everything in the folder is uploaded, not only the pages.

**Create the repository**

1. **Your helper signs in** to github.com with their account achooStorm.
2. In the upper-right corner, open the plus icon labeled "Create something new" and click **New repository** [S115].
3. In the **Owner** dropdown menu, choose achooStorm [S115].
4. In the "Repository name" field, type `hairbygerta` [S115]. The name becomes part of the preview address [S1], so type it exactly.
5. As the visibility, choose public [S3] [S115].
6. Do not let GitHub add a README, a license or a .gitignore file. GitHub says to leave them out when a folder that already exists is uploaded, to avoid errors [S116]. The folder has its own.
7. Click **Create repository** [S115].
8. Copy the address of the new repository from the Quick Setup page that opens [S116].

**Upload the folder**

9. Open a terminal in the folder `hairbygerta`. GitHub's page uses Git Bash on Windows [S116].
10. Type `git init -b main` and press Enter [S116]. This makes the folder a repository with a branch (a version of the files [S96]) called main.
11. Type `python tools/licensing_check.py --install-hook` and press Enter. This switches on the commit guard, the check that stops a Wix-only photo before every commit. Do not copy the guard file by hand.
12. Type `python tools/licensing_check.py` and press Enter. Go on only when it answers `Photo licensing check passed`.
13. Type `git add .` and press Enter [S116].
14. Type `git commit -m "First commit"` and press Enter [S116]. The guard runs again by itself. If it prints `PHOTO LICENSING CHECK: STOP`, stop here and do not go around it.
15. Type `git remote add origin REMOTE-URL` and press Enter. In place of REMOTE-URL, paste the address from step 8 [S116].
16. Type `git push -u origin main` and press Enter [S116]. If Git asks you to sign in, the helper signs in as achooStorm.

The name and the email address set in Git are saved with every commit, and anyone can see them in a public repository [S88].

**Turn on GitHub Pages**

17. On github.com, open the repository. Under its name, click **Settings**. If you cannot see it, open the dropdown menu and click **Settings** there [S94].
18. In the sidebar, in the section "Code, planning, and automation", click **Pages** [S94].
19. Under "Build and deployment", under "Source", select **Deploy from a branch** [S94].
20. In the branch dropdown menu, select `main` [S94].
21. In the folder dropdown menu, leave `/ (root)` selected [S94].
22. Click **Save** [S94].
23. Leave the "Custom domain" field empty. The domain comes later, in [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages).

**Wait for the build and look**

24. Wait up to 10 minutes [S3]. GitHub builds and publishes the site by itself, with a workflow run that the helper does not have to write [S94].
25. Go back to **Settings**, then **Pages**. Under "GitHub Pages", click **Visit site** [S3]. Or open https://achoostorm.github.io/hairbygerta/ directly [S1].
26. Click through every page, on a computer and on a phone.
27. Send Gerta the address, so she can look too.

If the address still does not open after an hour, look at the workflow runs of the repository: build and publishing errors show there [S94]. GitHub also says to make sure the push came from someone with admin rights and a verified email address [S3]. So check that the email address of the account achooStorm is verified.

From now on every push to main is published by itself [S94]. Always pull before you push, and never force a push: GitHub itself adds a file to the repository in Section 4.

## 2. What to check in Wix this week

You only look and write down. You change nothing in Wix. Use a computer, not a phone. Click only the buttons named in the steps. If a page asks you to pay, renew, cancel or confirm, close it.

Words used in this section:

- **Site plan**: the paid Wix plan that keeps the Wix site on hairbygerta.com. Wix also calls it a Premium plan [S19].
- **Domain**: the address of the website, hairbygerta.com.
- **Auto renew**: Wix charges your card by itself to keep a service running.
- **Business email**: the info@hairbygerta.com mailbox. Wix sells it through Google Workspace, Google's paid email service [S20].
- **Hover**: rest the mouse pointer on something without clicking.

Why three dates: canceling the site plan does not cancel the domain or the business email. Each has its own date [S19].

### Part A: End date of the Wix site plan

1. **Gerta signs in:** go to wix.com and sign in to the Wix account that owns the salon site.
2. Open the Wix help page "Viewing Your Site Plans and Other Subscriptions" at https://support.wix.com/en/article/viewing-your-premium-plans [S21].
3. Click **View Subscriptions**. The **Premium Subscriptions** page opens. It lists your plan and everything else you bought from Wix [S21].
4. Find the row of the site plan.
5. Read the **Upcoming payment** column in that row [S22].
6. Hover over the **Info** icon next to it [S22].
7. Write down the expiration date of the plan. If you only see a payment date, write that down and mark it "payment date".

The **Upcoming payment** column shows the next renewal payment, not the end of the plan [S22]. Wix plans renew by themselves at the end of the paid period unless they were canceled [S22]. With auto renew on, Wix may take the payment for a yearly plan up to 3 weeks before the plan's expiration date [S19] [S23]. So a date you see there can be a charge date that comes before the end of the plan.

Wix says a canceled plan stays active until the end of the paid period, and that its expiration date is shown on the Premium Subscriptions page [S19]. The help pages do not name the exact spot. If you see no date, copy what the row says word for word and show your helper. After the expiration date of a canceled plan the site address goes back to a free Wix address and Wix ads appear [S19].

Do not click **Turn Auto Renew On** this week. It switches a canceled plan back on [S24]. When that can be the right thing to do is in [Section 8, Part 1](#part-1-the-wix-site-plan-ends). That part also says what to do if the plan was never canceled and you do not want to pay Wix for another period.

### Part B: Expiry date of the domain

1. Click the user panel at the top right (the small menu for your own account) [S25].
2. Click **Account Settings** [S25].
3. Click **Domains** in the menu on the left [S25].
4. Find hairbygerta.com. Look under **Assigned Domains** first [S25].
5. Write down the expiry date and the payment renewal date. The page shows both [S25].
6. Open **Premium Subscriptions** again (Part A, steps 2 and 3).
7. Find the row of the domain.
8. Write down what its **Upcoming payment** column says [S26].
9. Write down whether the row says that auto renew is on or off for the domain. Wix's help pages do not name the spot where this shows. If you cannot tell, copy the row word for word and show your helper.

Check your date against the public record. On 13 October 2026 the registry (the organization that keeps the official list of all .com addresses) showed hairbygerta.com as registered through Wix.com Ltd. and expiring on 27 November 2026 at 01:04 UTC [S27]. UTC is the world's standard clock time. In New York that moment is 8:04 PM on 26 November 2026. So if Wix shows 26 November, it is the same moment. Your helper can look up the same record at https://lookup.icann.org [S28]. If Wix shows any other date, write down both. This date is close, so show it to your helper this week. What to do about it is in Section 3 under [Check your dates first](#check-your-dates-first).

Wix renews a domain bought from Wix by itself 30 days before it expires [S26]. So the payment renewal date can be a month earlier than the expiry date.

If hairbygerta.com is not on the Domains page, you are most likely signed in to a different Wix account. The help page from Part A, step 2 links to an account email locator [S21].

### Part C: End date of the business email

1. Stay on **Premium Subscriptions**.
2. Find the row of the business email.
3. Read the **Upcoming payment** column in that row [S29].
4. Hover over the **Info** icon next to it [S29].
5. Write down the expiration date. If you only see a payment date, write that down and mark it "payment date".
6. Open manage.wix.com/account/mailboxes. This is the Business Email page that Wix's help links to [S20].
7. Check that info@hairbygerta.com is listed there [S20]. If it is not, stop and tell your helper.

The Upcoming payment column shows the next renewal payment [S29]. Wix can take that payment up to 30 days before the mailbox expires [S30]. With auto renew off, the date shown can differ slightly from the expiration date [S29]. The mailbox only ends if it was canceled. Otherwise Wix renews it. What to do about that is in [Section 8, Part 3](#part-3-the-business-email-ends).

After the mailbox expires you can no longer read, receive or send email from it. Wix gives no number of days for how long the old mail is kept [S31]. So make the backup below well before that date. More on this is in [Section 8, Part 3](#part-3-the-business-email-ends).

### Part D: Back up the mailbox

You use **Google Takeout**, Google's tool for downloading a copy of your data [S32]. The Wix help pages about the business email give no steps for exporting mail [S30] [S31] [S33].

1. **Gerta signs in:** go to gmail.com and sign in with info@hairbygerta.com and its password [S33].
2. Go to takeout.google.com [S32].
3. Check that the picture or initial at the top right belongs to info@hairbygerta.com, not to a personal Gmail account. If it shows another account, click the picture or initial and select info@hairbygerta.com before you go on [S33].
4. Uncheck the box beside every product you do not need. Keep the box for your email (Gmail) checked. Keep Contacts, Calendar and Drive checked too if you use them [S32].
5. Select **Next step** [S32].
6. Under delivery method choose **Send download link via email** [S32].
7. Choose **One-time archive**. Archive is Google's word for the backup file [S32].
8. Choose **Zip files**. A zip file is one file that holds many files [S32]. Leave **Archive size** as it is. If your data is larger than that size, Google makes more than one file [S32].
9. Select **Create export** [S32].
10. Wait for the email from Google. It can take from a few minutes to a few days. Most people get it the same day [S32].
11. In that email select **Download archive** and follow the steps on the screen [S32]. If there is more than one file, download every one of them.
12. Save the file, or all the files, in a new folder called email-backup in your Documents. Never save them in the `hairbygerta` folder, because the files in that folder are published as the public website.
13. Copy the file or files to a USB stick as well.

Do steps 11 to 13 within a week. The archive expires in about 7 days and can be downloaded 5 times [S32].

Mail that arrives after the export is not in the file. So do Part D now, and one last time later: right after the email forwarding in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) works, or about one week before the business email end date, whichever comes first. Do not leave it to the last days. The export can take a few days [S32], and after the end date you can no longer open the mailbox to get the download link [S31].

If Takeout says you cannot download, stop and tell your helper. Takeout is allowed by default for Google Workspace, but an administrator can block it [S34].

### Write it down

Write the month as a word, for example 27 November 2026.

| What | Where you read it | Date | What the Upcoming payment column says |
|---|---|---|---|
| Wix site plan ends | Premium Subscriptions | | |
| Domain hairbygerta.com expires | Domains | | |
| Domain payment renewal date | Domains | | |
| Domain auto renew | Premium Subscriptions | not needed | write "on" or "off" here |
| Business email ends | Premium Subscriptions | | |
| Mailbox backup made on | your own note | | not needed |

## 3. Moving the domain from Wix to Cloudflare Registrar, step by step

**Who signs in.** Every step in this section that starts with **Gerta signs in** follows the rule at the top of this guide: Gerta does it herself, or her helper does it with Gerta next to them. Nobody asks for her passwords or her transfer code. Wix itself lets only the site owner move a domain away (a co-owner only if they own the payment method used for the domain) [S35].

### Read this first: it takes two moves, not one

Five words used below:

- **Cloudflare**: the company that will hold the domain's settings after the first move, and the domain itself after the second.
- **Registrar**: the company where a domain is registered and renewed. For hairbygerta.com that is Wix today [S27].
- **Nameservers**: the two addresses that say which company holds a domain's settings.
- **DNS records**: those settings, a list that tells the internet where the website is and where the email goes.
- **Authorization code** (also called EPP code): a one-time password that lets a domain move to another registrar.

What the official pages say:

- Cloudflare Registrar only accepts a domain that is already active in Cloudflare. That means its nameservers were changed to Cloudflare's first [S36].
- Wix does not let you change the nameservers of a domain bought from Wix [S37].
- So Cloudflare's guide says a domain cannot go straight from Wix to Cloudflare Registrar. Its route is: move the domain to another registrar, set Cloudflare's nameservers there, wait 60 days, then move it to Cloudflare Registrar [S36]. In this guide the other registrar is called the in-between registrar.
- After the first move the website and email settings already run on Cloudflare. Cloudflare says you can stop there if that is all you need [S36].
- There is also a simpler way. Wix says a Wix domain can stay registered at Wix and be pointed to a site hosted elsewhere, with no transfer [S38] [S39]. Know one thing before you choose it: the domain's settings then stay at Wix [S37], and the free email forwarding in Section 5 only works with the settings at Cloudflare [S40]. Sections 4 and 5 are written for the route with two moves.

Decide with your helper before you start.

### The rules today

- **The 60-day lock.** ICANN (the organization that sets the rules for domain names) lets a registrar refuse a transfer in the first 60 days after a domain is registered and in the 60 days after an earlier transfer. It requires a 60-day lock after the owner's name, organization or email is changed, unless the registrar offered an opt-out beforehand [S41] [S42]. Wix and Cloudflare both apply the 60 days [S35] [S36] [S38]. A proposal to shorten this to 30 days is not in force: ICANN's published policy still says 60 days, and its review page lists the Board decision as "TBD" [S41] [S43].
- **Time.** Wix says a transfer away usually takes up to 7 days [S35]. Cloudflare says a first move like this usually takes 3 to 5 days, and a move into Cloudflare up to 10 days in all [S36]. Under ICANN's policy, if the old registrar does not answer within five calendar days, the transfer goes through [S41].
- **Cost.** Each move adds one year to the domain, and you pay the registrar that receives it [S36]. Cloudflare charges what the domain costs it, with no markup [S36] [S44]. On 12 October 2026 its domain search showed a .com name at \$10.46, with the line **Renews at \$10.46/year** [S44]. How to check today's price is in [Section 9](#the-domain-the-one-bill). You also see the price on the screen before you buy [S44]. The in-between registrar sets its own price: read it on its website. Wix does not refund domain payments [S45].

### Check your dates first

Use the dates you wrote down in [Section 2](#write-it-down). Wix shows them on the **Premium Subscriptions** page, in the **Upcoming payment** column next to the domain and next to the site plan [S23] [S26].

What the dates mean:

- Wix renews a domain automatically 30 days before it expires, and a yearly site plan up to 3 weeks before it expires [S23] [S26].
- The public record for hairbygerta.com, read on 13 October 2026, shows: registrar Wix.com Ltd., registered 27 November 2025, expires 27 November 2026 at 01:04 UTC, transfer lock on, DNSSEC on [S27]. In New York that expiry moment is the evening of 26 November 2026. You can look the record up yourself at https://lookup.icann.org [S28] [S42]. Part B says what to do about the lock and about DNSSEC (a security seal on the domain's settings). If the record is right, the first 60 days are long over, and Wix will charge the renewal around 27 October 2026 unless auto renew is off.
- Cloudflare warns that a domain that is renewed and then moved too soon may not get the extra year of the move. You would then pay for the same year twice [S46]. Its pages count the 45 days of waiting from the renewal [S46] and from the original expiration date [S36] [S47]. Cloudflare says this is a rule of the registry and holds for every registrar [S46].
- Start the first move at least 2 to 3 weeks before the earliest Wix end date you wrote down. A move can take a week, and a first try can fail.
- Look at the business email end date too. After that date the mailbox no longer receives mail [S31]. The free forwarding in Section 5 can only be turned on once the domain's settings are at Cloudflare [S40], which is after the first move. If the business email ends before that, mail to info@hairbygerta.com does not arrive in between. Plan the first move so that this cannot happen, or ask your helper.

Pick one of these two ways with your helper, before the domain's **Upcoming payment** date.

**Cheaper:** turn off auto renew and finish the first move before the domain expires.

1. **Gerta signs in** to Wix and goes to **Premium Subscriptions** [S45].
2. Click the **More Actions** icon next to the domain [S45].
3. Click **Cancel domain** [S45].
4. Select **Cancel auto renew** [S45].
5. Click **Submit** [S45].

You keep the domain until the end of the paid period [S45]. If the public record above is right, start Part B no later than 6 November 2026. If the domain expires first, Wix says it can only be moved while it is in its Grace Period [S35]. What an expired domain means is in [Section 8, Part 2](#part-2-the-domain-expires). Read it before you choose this way.

**Calmer:** let Wix renew the domain for one more year. Afterwards, check on the **Domains** page that the expiry date now says 2027. How to renew by hand, and what happens if the payment fails, is in [Section 8, Part 2](#part-2-the-domain-expires). Then wait until at least 45 days after the domain's old expiry date before you start Part B. That is the later and safer of Cloudflare's two ways of counting [S36] [S46]. If the public record is right, that means not before 11 January 2027. If your site plan ends before then, the domain can be pointed to the new site from inside Wix in the meantime [S39].

### Part A: Get Cloudflare ready

Nothing in Part A changes what visitors see.

1. **Gerta signs in:** go to https://dash.cloudflare.com/sign-up [S48].
2. Type your own email in **Email** and a new password in **Password** [S48]. Use a personal address, not info@hairbygerta.com. The reason is the same as for the Square login in Section 1, Part 3: the address must keep working while the domain moves.
3. Click **Create Account** [S48].
4. Open the email from Cloudflare and open the link in it. This verifies your address [S49].

Do steps 5 to 11 in the same week you start Part B. Cloudflare deletes a Free-plan domain that is still waiting for its nameservers after 28 days [S50].

5. **Gerta signs in** to Cloudflare and goes to **Domains** [S51].
6. Select **Onboard a domain** [S51].
7. Type hairbygerta.com, let Cloudflare scan for DNS records, and select **Continue** [S51].
8. Choose the **Free** plan [S51].
9. **Gerta signs in** to Wix to see the same list there: **Domains**, then the **Domain Actions** icon next to the domain, then **Manage DNS Records** [S39]. Cloudflare's scan can miss records [S36].
10. Make sure every email record (the lines whose Type is MX or TXT) is in Cloudflare exactly as Wix shows it. To add one, click **Add record** on the **DNS Records** page, pick the **Type**, fill it in and click **Save** [S52]. Wix says email stops working after a transfer until the MX records are added again [S35]. The website records are covered in [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages).
11. Write down the two nameservers Cloudflare gives you. They are also on the domain's **Overview** page [S51].
12. Choose the in-between registrar. It must let you change nameservers [S36]. This guide does not pick one. Read its price and its steps for transferring a domain in on its own help pages. **Gerta signs in** to create the account there, with the same personal email address.

### Part B: First move, from Wix to the in-between registrar

Start only when the new site is published at the preview address and you have checked every page there. Once the domain has been transferred away, Wix disconnects your Wix site from it [S35].

Before you click, know two things:

- Wix sells privacy and DNSSEC as one switch [S53]. Turning it off makes your name and contact details visible to anyone in the public record (Whois) [S53]. Only Gerta can decide whether she accepts that. If she does not, stop here and use the simpler way under [Read this first](#read-this-first-it-takes-two-moves-not-one).
- On the **Edit contact info** page, change nothing else and save nothing else. Wix says that changing the contact information locks the domain for 60 days [S38] [S54].

1. **Gerta signs in** to Wix and goes to **Domains** [S53].
2. Click the **Domain Actions** icon next to hairbygerta.com [S53].
3. Click **Edit contact info** [S53]. Read the email address shown for the registrant contact (the owner of the domain) and write it down. Wix sends the transfer code to that address [S35]. If Gerta cannot open that mailbox, stop and ask your helper. Changing the address locks the domain for 60 days and has to be confirmed from both the old and the new address [S54].
4. Click **Show more** next to **Privacy and DNSSEC protection** [S53].
5. Click **Turn off protection** [S53].
6. Click **Turn Off Protection** to confirm [S53].
7. Wait at least 24 hours [S36].

Why steps 1 to 7: Cloudflare says to turn DNSSEC off before the nameservers change, or the domain can become unreachable [S36] [S51]. Wix advises turning privacy off before a transfer anyway, so you do not miss emails about it [S35]. After step 7, have the public record checked again [S27]. If it still shows DNSSEC on, ask Wix Customer Care before you go on.

8. **Gerta signs in** to Wix, goes to **Domains** and clicks the **Domain Actions** icon again [S35].
9. Select **Transfer away from Wix** [S35].
10. Read the page and click **Transfer Domain** [S35].
11. Click **I Still Want to Transfer** [S35].
12. **Gerta opens the mailbox of the address from step 3.** Wix sends the authorization code to the registrant contact email of the domain [S35]. Keep it as private as a password. Use it soon, because codes expire [S36].
13. **Gerta signs in** at the in-between registrar and follows its steps to transfer a domain in. It will ask for the code and for payment [S35] [S36]. If it asks for the contact details of the domain's owner, type your real ones, with an email address that you can open and that does not end in @hairbygerta.com. Wix itself recommends a contact email address that is not tied to the domain [S54].
14. Wait. If Wix or the new registrar emails you to ask for approval, approve [S35] [S36]. While the move runs, the Status in Wix's Whois Lookup tool shows "pending transfer" [S35]. The Wix help page behind that marker links to the tool.
15. On the day the move completes, **Gerta signs in** at the in-between registrar and replaces its nameservers with the two from Part A. Copy them exactly [S51].
16. Wait up to 24 hours. Cloudflare emails you, and the domain shows **Active** on the **Domains** page [S51].
17. In the two weeks after the move, watch your inbox, spam folder included, for an email from the in-between registrar that asks you to confirm (verify) the contact email address of the domain. Open the link in it at once. ICANN requires a registrar to check the owner's email address or phone number within 15 days of a transfer. A registrar that gets no answer has to check by hand or suspend the domain [S55]. A suspended domain shows no website and receives no email. If no such email comes, there is nothing to do.

Wix's guide shows no separate unlock button [S35]. If the in-between registrar says the domain is still locked, ask Wix Customer Care to unlock it. ICANN's policy gives a registrar five calendar days to remove the lock and hand over the code after you ask [S41] [S42].

Between the end of the move and step 16 the web address and the email may not work for a while [S35]. So do step 15 at once. Do not pause after step 16 either. Go straight on to [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages). Keep watching for the email of step 17 in the meantime. Until Section 4 is done, hairbygerta.com may show no website. You do not have to wait for Part C and Part D first: Cloudflare says its DNS can be used as soon as the nameservers are set [S36].

### Part C: Wait 60 days

1. Mark the date 60 days after the first move completed [S36].
2. Until then, do not change the owner's name, organization or email for the domain. That starts another 60-day lock [S36].

### Part D: Second move, into Cloudflare Registrar

1. **Gerta signs in** to Cloudflare and goes to **Billing**, then **Subscriptions**, then **Payment methods** [S56].
2. Click **Add Payment Method** and enter your own card or PayPal [S56].
3. Click **Confirm** [S56].
4. **Gerta signs in** at the in-between registrar and removes the transfer lock on the domain [S36].
5. Ask the in-between registrar for the authorization code [S36].
6. **Gerta signs in** to Cloudflare and goes to **Transfer domains** [S36].
7. Select hairbygerta.com and enter the code [S36]. Read the price on the screen first. Cloudflare charges your payment method when you enter the code and start the transfer, and its FAQ says registration and renewal payments are not refunded [S46].
8. Type your own contact details: your real name, address and phone number, and an email address you can open. Use the email address of your Cloudflare account, not info@hairbygerta.com. ICANN requires the details to be accurate, and wrong details can get the domain suspended. Cloudflare keeps them out of the public record by default [S36].
9. Read the domain registration terms shown on the screen. Selecting **Confirm transfer** means that Gerta agrees to them, so only she decides this [S36].
10. Select **Confirm transfer** [S36].
11. **Gerta approves** the transfer when the in-between registrar emails her, or in its dashboard. Without approval it can take up to five days to release the domain [S36] [S46].
12. Check the **Transfer domains** page until the move is complete [S46].
13. Watch your inbox, spam folder included, for an email from Cloudflare that asks you to verify the contact email address of the domain. Open the link in it at once. If the address is not verified within 15 days, Cloudflare puts a hold on the domain and swaps its nameservers for a parking server until you verify [S47]. The website and the email stop for that time. Cloudflare sends this email when the contact email address differs from the verified email address of the Cloudflare account [S47]. If no such email comes, there is nothing to do.

From then on the domain renews at Cloudflare and must keep Cloudflare's nameservers [S46]. What that costs each year is in [Section 9](#9-yearly-cost-after-the-move).

### If something goes wrong: point the domain back to the Wix site

This only works while your Wix site plan is active, because Wix needs an upgraded site to connect a domain [S57]. It sends visitors back to the Wix site. It does not move the registration back to Wix [S58].

Before the first move completes, the website needs no undoing: Wix disconnects the site only once the domain has been transferred [S35]. But two things you changed on the way stay changed:

- If you turned auto renew off under [Check your dates first](#check-your-dates-first) and you give up the move, turn auto renew back on before the domain's end date, or the domain expires. Wix says you can turn auto renew back on before the end of the subscription period [S59]. Its page does not give the clicks for a domain. If you cannot find the switch on the **Premium Subscriptions** page, ask Wix Customer Care.
- You can switch Privacy and DNSSEC protection back on with **Turn On Protection**, on the page where you turned it off [S53].

After the domain has left Wix:

1. **Gerta signs in** to Wix, goes to **Domains** and clicks **Add an Existing Domain** [S57].
2. Click **Connect a domain you already own** [S57].
3. Select the site and click **Continue** [S57].
4. Type hairbygerta.com and click the arrow [S57].
5. Click **connect it to your site** below the search field [S57]. If a **Start Transfer** option appears, do not click it. Click **connect your domain** in the sentence below it [S57].
6. Click **go to our manual setup** [S57].
7. Click **Start** [S57].
8. Click **pointing** at the top [S57].
9. Click **Switch to Pointing Instructions** [S57]. Wix opens a step by step outline. Leave it open [S57].
10. In a new tab, **Gerta signs in** to Cloudflare and opens the **DNS Records** page [S52].
11. Back in the Wix outline, click **I logged in** [S57].
12. Click **I found my domain settings** [S57].
13. Click **I found the records** [S57]. Wix now gives you its A record and its CNAME record (the two settings that say where the website is) [S57].
14. In Cloudflare, click **Edit** next to the A record for hairbygerta.com [S52]. If Section 4 was done before, there are four such A records. Pick any one of them.
15. Type the value Wix shows, set **Proxy status** to **DNS only** and click **Save** [S52] [S60].
16. Do steps 14 and 15 again for the CNAME record for www [S52].
17. Delete every other A or CNAME record for those two names: **Edit**, then **Delete**, then **Delete** again [S52]. Wix says to replace your records with its own, not to add to them [S57].
18. Back in the Wix outline, click **I updated my records** [S57].
19. Wait up to 48 hours [S57].

Wix's page today lists A record 185.230.63.107 and CNAME www to pointing.wixdns.net. Trust the values on your own Wix screen [S57]. **DNS only** and DNSSEC off are needed because Wix supports neither Cloudflare's proxy nor DNSSEC [S57].

If the domain was already pointed at the new site (Section 4), also take the domain out of GitHub afterwards. Those are steps 3 to 5 under [How to undo the switch](#how-to-undo-the-switch) in Section 4.

## 4. After the transfer: pointing the domain at GitHub Pages

This is the switch. When it is done, www.hairbygerta.com shows the new site from GitHub instead of the Wix site. Your helper changes one setting in GitHub, and Gerta changes a few lines in Cloudflare. Do it together. The work takes about 20 minutes, then you wait. Nothing is changed in Wix or in the `hairbygerta` folder on your computer.

"The transfer" in the title is the first move of the domain (Section 3, Part B). You do not wait for the second move.

Words used in this section:

- **DNS records**: the list of settings that tells the internet where the website is and where the email goes. After the first move you edit that list in Cloudflare.
- **A record**: a DNS record that points a name at the number address of a server. AAAA is the same thing for a newer kind of address [S61].
- **CNAME record**: a DNS record that points a name at another name [S61].
- **HTTPS**: the secure form of a web address, the one that starts with https://.
- **Security certificate**: the proof behind HTTPS. GitHub requests one for your domain by itself [S62].
- **Repository**: the project on GitHub that holds the site files [S63].

### Whose GitHub account this is, and what Gerta decides

The new site is in the GitHub account achooStorm. That account belongs to your helper, not to Gerta. In plain words:

- **The helper does every GitHub step.** The helper signs in to their own account. Gerta cannot do these steps alone, and she needs the helper again for every later change on GitHub. Only a person with admin rights for the repository can set the domain there [S64].
- **The address stays Gerta's.** The domain's settings are in Gerta's own Cloudflare account (Section 3). The DNS records of Part 3 point her address at the site in the helper's account. Gerta can change those records herself, as [How to undo the switch](#how-to-undo-the-switch) shows.
- **The site files are in the helper's account.** Ask your helper for a copy of the folder `hairbygerta` and keep it, so that the site can be published from another account if the two of you ever stop working together.
- **Gerta's decision: verifying the domain.** GitHub recommends verifying the domain [S64]. That is the optional lock at the end of this section. Verifying ties hairbygerta.com to the helper's GitHub account. From then on only repositories owned by that account may publish a GitHub Pages site at hairbygerta.com or at a name directly under it, such as www.hairbygerta.com [S66]. This protects the address from strangers [S66]. It also binds the address, on GitHub, to an account that is not Gerta's. The TXT record that keeps the domain verified is in Gerta's Cloudflare account [S66]. GitHub's page does not say how a verification is taken off again [S66]. Whether to do this is Gerta's decision alone. The helper verifies the domain only after Gerta has clearly said yes.

### Before you start the switch

- The first move in Section 3 is finished ([Part B](#part-b-first-move-from-wix-to-the-in-between-registrar), step 16): hairbygerta.com shows **Active** in Cloudflare [S51].
- The new site looks right at the preview address https://achoostorm.github.io/hairbygerta/.
- Your helper is there to sign in to GitHub. The account achooStorm is the helper's, and only a person with admin rights for the repository can set the domain there [S64].
- You do this as soon as the first move is finished, without waiting for a quiet day. Wix disconnects the Wix site from the domain once the domain has been transferred away [S35], so the address may show no website until this section is done. The secure address can take up to an hour to start working [S65].
- Optional, and recommended by GitHub before Part 2: lock the domain to the helper's GitHub account first [S64]. Gerta has decided this beforehand, yes or no (see the part above). See [Optional: lock the domain to the GitHub account](#optional-lock-the-domain-to-the-github-account). It takes about ten minutes of work and then a wait of up to 24 hours [S66]. If the address already shows no website, do Parts 1 to 4 first and the lock straight after. If GitHub says in Part 2 that the domain is already taken, do the lock before you go on [S65].

### Part 1: Save a copy of today's DNS records

You need this copy if you ever undo the switch.

1. **Gerta signs in** to Cloudflare.
2. Open the **DNS Records** page for hairbygerta.com. Cloudflare's help page gives this direct link: https://dash.cloudflare.com/?to=/:account/:zone/dns/records [S52].
3. Take a screenshot or a phone photo of the whole list.
4. Select **Import and Export** [S67].
5. Select **Export** [S67].
6. Keep the downloaded file together with the screenshot. Do not save either of them in the `hairbygerta` folder.

### Part 2: Tell GitHub the domain

GitHub says to do this before the DNS change. Otherwise someone else could host a site on your www address in between [S64].

1. **Your helper signs in** to github.com with their account achooStorm.
2. Open https://github.com/achooStorm/hairbygerta.
3. Under the repository name, click **Settings**. If you cannot see it, open the dropdown menu with the three dots at the end of that row and click **Settings** there [S64].
4. In the sidebar, in the section "Code, planning, and automation", click **Pages** [S64].
5. Under "Custom domain", type `www.hairbygerta.com` [S64].
6. Click **Save** [S64].

Two things happen now:

- GitHub starts a DNS check [S62]. It cannot pass yet, because the DNS records do not point to GitHub yet. If GitHub shows a warning now, carry on with Part 3.
- GitHub adds a small file named CNAME to the repository, because the site is published from a branch [S64]. Never delete it, or the site stops showing at the domain [S65]. Before the next upload from the `hairbygerta` folder, pull first (pull means: fetch GitHub's latest version into the folder), so the folder has that file too [S64]. [Section 6, Part A](#part-a-get-the-latest-version) shows how.

### Part 3: Change the DNS records in Cloudflare

First remove the old website records. GitHub says leftover records of these kinds can stop the security certificate [S62]. Do steps 1 to 12 in one go: between deleting and adding, the domain shows no website.

1. Open the **DNS Records** page again [S52].
2. Find a record whose Type is A, AAAA or CNAME and whose Name is `hairbygerta.com`, `@` or `www`.
3. On that record, select **Edit** [S52].
4. Select **Delete** [S52].
5. Select **Delete** again to confirm [S52].
6. Repeat steps 2 to 5 until no such record is left.

Leave every other record alone, above all MX and TXT. MX records deliver your email [S61]. Email is the subject of [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail).

Now add the five new records.

7. Select **Add record** [S52].
8. Choose the **Type** shown in the first row of the table below [S52].
9. Fill in **Name** and the address or target from the same row [S61].
10. Set **Proxy status** to **DNS only** [S60].
11. Select **Save** [S52].
12. Repeat steps 7 to 11 for the other four rows.

| Type | Name | Fill in | Proxy status | TTL |
|---|---|---|---|---|
| A | `@` | IPv4 address `185.199.108.153` | DNS only | Auto |
| A | `@` | IPv4 address `185.199.109.153` | DNS only | Auto |
| A | `@` | IPv4 address `185.199.110.153` | DNS only | Auto |
| A | `@` | IPv4 address `185.199.111.153` | DNS only | Auto |
| CNAME | `www` | Target `achoostorm.github.io` | DNS only | Auto |

- `@` means the bare domain, hairbygerta.com without www [S61] [S68]. After you save, the list may show this name as `hairbygerta.com` instead of `@`. That is the same record [S51].
- The four addresses are GitHub's own. They were checked against the GitHub help page on 13 October 2026 [S64]. Check them there again on the day you do this.
- The target is `achoostorm.github.io` and nothing more. Do not add `/hairbygerta` [S64].
- TTL is how long other computers remember a record. Leave it on Auto.
- **DNS only** shows a gray cloud. **Proxied** shows an orange cloud [S60]. Cloudflare turns the proxy on by default when a domain is added, so check all five rows [S60].

Why DNS only: the proxy puts Cloudflare between your visitors and the site. With the proxy on, Cloudflare answers with its own addresses instead of GitHub's [S60]. GitHub checks your DNS records before it creates the security certificate, and records that do not point to GitHub can block it [S62]. Cloudflare's own advice for a site hosted on another company's platform is DNS only unless that platform says it supports the proxy, because visitors can otherwise get security errors or endless redirects, where the page keeps sending the browser in a circle [S69]. GitHub's help pages on custom domains and HTTPS do not mention Cloudflare or a proxy at all [S62] [S64] [S65] [S66] [S70]. Cloudflare recommends the proxy for most other websites [S60], so this is a deliberate exception.

### Part 4: Wait for the check, then turn on HTTPS

1. In GitHub, go back to **Settings**, then **Pages** [S64]. If GitHub asks you to sign in again, the helper does it, as in Part 2.
2. Reload the page from time to time until a check mark shows beside `www.hairbygerta.com` [S62].
3. Under "GitHub Pages", select (tick) **Enforce HTTPS** [S62]. From then on everyone is sent to the secure address [S62].

If there is still no check mark after an hour, restart the check [S62]. GitHub says this can be needed after DNS records were changed [S65].

1. Click **Remove** next to the custom domain [S62].
2. Type `www.hairbygerta.com` again.
3. Click **Save** [S62].

### How long it takes

- The DNS change: other computers keep a Cloudflare record on Auto for 5 minutes. Your own computer may hold the old answer longer [S71]. GitHub says to allow up to 24 hours [S64].
- The secure address: up to an hour after the domain is set [S65].
- The **Enforce HTTPS** box: it can take up to 24 hours before you can tick it [S64].

### What you see when it has worked

- In GitHub under **Settings**, **Pages**: a check mark beside www.hairbygerta.com [S62], and **Enforce HTTPS** is ticked. This is the check to trust.
- https://www.hairbygerta.com opens the new site. The two sites look alike. As long as some placeholders are left, you can tell the new site by its beige boxes.
- hairbygerta.com without www jumps to www.hairbygerta.com by itself [S64].
- The old page addresses still open, for example https://www.hairbygerta.com/gallery/ and https://www.hairbygerta.com/book-online/.
- If you still see the Wix site, clear your browser's cache (the copies of pages it keeps) and look again [S65].

### If it has not worked after 24 hours

- Compare the DNS Records page with the table in Part 3: Type, address or target, and Proxy status, letter by letter. A Name shown as `hairbygerta.com` is the `@` of the table. Delete any other A, AAAA or CNAME record named `hairbygerta.com`, `@` or `www` [S62]. Then restart the check as in Part 4.
- The browser says "too many redirects" or shows a security warning: check that none of the five records is set to Proxied [S69]. If one is, select **Edit** on it, set **Proxy status** to **DNS only** and select **Save** [S52].
- The list has records of Type CAA (they name who may issue certificates for the domain): at least one of them must contain `letsencrypt.org` [S65]. If there are none, there is nothing to do.
- GitHub says the domain is already taken: the optional lock below frees the domain for the helper's account [S65]. It is still Gerta's decision.

### How to undo the switch

This puts the Wix site back on the domain. Wix only connects a domain to a site that is upgraded [S57]. So it only works before the end date of the Wix site plan that you wrote down in [Section 2](#write-it-down).

1. Do the steps under [If something goes wrong: point the domain back to the Wix site](#if-something-goes-wrong-point-the-domain-back-to-the-wix-site) in Section 3. They connect the domain to the Wix site again. They also change the website records in Cloudflare to the values Wix shows and delete the rest of the five records you added in Part 3. Cloudflare's own note on Wix says the same: connect by pointing, with every record set to **DNS only** [S72].
2. Compare the website records with your screenshot from Part 1. The values on your Wix screen are the ones that count [S57].
3. **Your helper signs in** to GitHub, opens the repository and goes to **Settings**, then **Pages** [S64].
4. Under "Custom domain", the helper clicks **Remove** [S64]. Do this last. GitHub warns that DNS records pointing at GitHub with no domain set there could let someone else put a site on your name [S64].
5. Wait. Wix says it may take up to 48 hours [S57].

The pages of the Wix site and the `hairbygerta` folder on your computer were never changed, so there is nothing else to undo.

### Optional: lock the domain to the GitHub account

This is called verifying the domain. It stops other GitHub users from taking over your domain for a site of their own [S66]. It also ties hairbygerta.com to your helper's GitHub account achooStorm, because that is the account that verifies it [S66]. Do it only if Gerta has said yes. What she decides is explained under [Whose GitHub account this is, and what Gerta decides](#whose-github-account-this-is-and-what-gerta-decides). GitHub recommends doing it before Part 2 [S64]. If you did not do it then, do it as soon as Part 4 is finished.

The helper does steps 1 to 7 and step 11 in GitHub. Gerta does steps 8 to 10 in Cloudflare.

1. **Your helper signs in** to github.com with their account achooStorm and clicks the profile picture in the upper-right corner [S66].
2. Click **Settings**. These are the profile settings of the helper's account, not the repository settings [S66].
3. In the sidebar, under "Code, planning, and automation", click **Pages** [S66].
4. Click **Add a domain** [S66].
5. Type `hairbygerta.com` under "What domain would you like to add?" [S66].
6. Select **Add domain** [S66].
7. Leave this page open. Under "Add a DNS TXT record" it shows a name and a value [S66]. A TXT record is a DNS record that holds a line of text [S61].
8. **Gerta signs in** to Cloudflare. On the **DNS Records** page, select **Add record** and choose the Type TXT [S52].
9. Copy the name from GitHub into **Name** and the value from GitHub into **Content** [S61].
10. Select **Save** [S52].
11. Back on GitHub, click **Verify** [S66]. The DNS change can take up to 24 hours [S66]. If you left the page in the meantime, open the three-dot menu to the right of the domain and click **Continue verifying** first [S66].
12. Keep that TXT record for as long as the domain should stay verified. It is what keeps the domain verified [S66].

## 5. Free email forwarding from info@hairbygerta.com to Gmail

Cloudflare **Email Routing** takes mail that is sent to info@hairbygerta.com and forwards it to a mailbox you already have, here your Gmail [S40]. It is a forwarder, not a mailbox: it only receives. To send mail from your domain as well you would need a separate mail provider [S73]. Cloudflare's pricing page lists incoming email as Unlimited on its free plan (Workers Free) [S74]. If a screen asks for a card or a paid plan, stop and ask your helper.

Why you need it: the form on the Contact page of the new site does not deliver messages by itself. It opens the visitor's own email app with a message addressed to info@hairbygerta.com. The email links on the site do the same. If this forwarding does not work, those messages never reach you.

Words used in this section:

- **DNS records**: the list of settings that tells the internet where the website is and where the email goes.
- **MX record**: a DNS record that says which mail servers receive the domain's mail.
- **TXT record**: a DNS record that holds one line of text. Mail systems read it to check who may handle the domain's mail.
- **Destination address**: the mailbox the mail is forwarded to, here your Gmail address [S75].
- **Routing rule**: one line that says "mail for this address goes to that destination" [S75].
- **Onboard**: Cloudflare's word for signing a domain up for this service.

### Before you turn on forwarding

- The domain's DNS is at Cloudflare. Email Routing works only then [S40]. That is the case once the first move in Section 3 is finished ([Part B](#part-b-first-move-from-wix-to-the-in-between-registrar), step 16).
- You have a Gmail address of your own and can open its inbox. Below it is called "your Gmail address".
- The mailbox backup from [Section 2, Part D](#part-d-back-up-the-mailbox) is done.
- Today's date is before the business email end date you wrote down in [Section 2, Part C](#part-c-end-date-of-the-business-email). After that date the business email can no longer receive mail [S31], so forwarding must be working by then.
- info@hairbygerta.com is the only address ending in @hairbygerta.com that you use. Forwarding takes over the mail for the whole domain, and only an address with a routing rule is forwarded [S75] [S76]. If you have another address or an alias (a second name for the same mailbox), tell your helper before Part 1. It needs its own rule (Part 3), or the **Catch-all rule** on the **Routing Rules** tab, which forwards every email sent to the domain to one destination [S75].

One thing changes when you turn it on. Today, mail for info@hairbygerta.com lands in the business email, the paid mailbox from Wix. On 12 October 2026 the domain's MX records pointed to Google's mail servers [S77]. Email Routing needs Cloudflare's own MX records, and Cloudflare says it cannot be used together with another mail server [S76]. So from the moment you turn it on, new mail for info@hairbygerta.com goes to your Gmail and no longer to the business email. As long as the business email is still paid, your helper can undo this: see [For your helper](#for-your-helper).

Do Parts 1 to 3 in one sitting, so the address is never left without a rule.

### Part 1: Turn on Email Routing for the domain

1. **Gerta signs in** to the Cloudflare dashboard (Cloudflare's control panel) at https://dash.cloudflare.com and selects her account [S75].
2. Go to **Compute**, then **Email Service**, then **Email Routing** [S40]. Cloudflare's help page gives this direct link: https://dash.cloudflare.com/?to=/:account/email-service/routing [S40].
3. Select **Onboard Domain** [S40].
4. Choose hairbygerta.com [S40].
5. If the screen lists the DNS records Cloudflare will add, read them [S40]. They are explained in Part 4.
6. Select **Done** [S40].
7. Whatever the screen said, have your helper open the **DNS Records** page now [S52]. hairbygerta.com came to Cloudflare with five Google MX records and one Google SPF record [S77]. Email Routing requires Cloudflare's MX records, and existing MX records have to be removed or updated [S76]. For the name hairbygerta.com the list must show only the three MX records ending in `.mx.cloudflare.net`, and exactly one TXT record that starts with `v=spf1` [S76] [S78].

If the list shows anything else, or if the screen reported a problem with existing MX or SPF records, stop. Show your helper the part [For your helper](#for-your-helper) below.

### Part 2: Add your Gmail address and confirm it

1. Go to **Compute**, **Email Service**, **Email Routing**, then **Destination Addresses** [S40].
2. Under **Destination addresses**, type your Gmail address into the form and submit it [S40].
3. Open your Gmail inbox.
4. Open the verification email from Cloudflare [S40]. Look in the spam folder if you do not see it.
5. In that email, select **Verify email address** [S40].

Nothing is forwarded before step 5. A routing rule stays disabled until its destination address is verified [S75]. If the email never comes, the **Destination Addresses** page lists the address as pending and lets you resend the email [S75].

### Part 3: Create the address info@hairbygerta.com

1. Go to **Compute**, **Email Service**, then **Email Routing** [S40].
2. Select hairbygerta.com [S40].
3. Select the **Routing Rules** tab [S40].
4. Select **Create routing rule** [S40].
5. In **Email pattern**, type `info` and select hairbygerta.com [S40].
6. In **Action**, choose **Send to an email** [S40].
7. In **Destination**, choose your Gmail address [S40].
8. Select **Save** [S40].

The status button of the rule must show **Active**, not **Disabled** [S75].

### Part 4: The DNS records Cloudflare adds

You do not type these. Cloudflare adds them to the bare domain (hairbygerta.com without www) when you onboard the domain [S76].

| Type | Name | Content | What it is for |
|---|---|---|---|
| MX, three records | `@` | Cloudflare mail servers, names ending in `.mx.cloudflare.net` | Sends the domain's incoming mail to Cloudflare [S76] |
| TXT | `@` | `v=spf1 include:_spf.mx.cloudflare.net ~all` | Called SPF. Allows Cloudflare to forward mail for your domain [S76] |
| TXT | `cf2024-1._domainkey` | A long key that Cloudflare supplies | Called DKIM. A signature that shows forwarded mail is genuine [S76] |

To see them:

1. Go to **Compute**, **Email Service**, then **Email Routing** [S76].
2. Select hairbygerta.com, then open **Settings** [S76].
3. Look at the **DNS records** section. Each record shows **Locked** or **Unlocked**. Both mean the record is set up correctly [S76].

Leave these records alone. A locked record cannot be edited or deleted on the **DNS** > **Records** page until it is unlocked [S76]. DNS changes usually take 5 to 15 minutes and can take up to 24 hours [S40].

### Part 5: Test the forwarding

1. Ask a friend to send an email to info@hairbygerta.com. Do not send it from your own Gmail address. Cloudflare warns that some providers discard a message that seems to come from the account it is delivered to [S40].
2. Check your Gmail inbox [S40].
3. If it is not there, check the spam folder [S40].
4. Reply to the message. Ask your friend which address the reply came from. It will be your Gmail address. The reason is under [Limits of the forwarding](#limits-of-the-forwarding).
5. Test the form of the new site the same way. Ask your friend to open its Contact page, fill in the form and select **Send**. The page is https://www.hairbygerta.com/contact/ once the domain points to the new site, and https://achoostorm.github.io/hairbygerta/contact/ before that. Their email app opens with a message to info@hairbygerta.com. They send it, and you check your Gmail.
6. When both tests have worked, back up the business email one last time ([Section 2, Part D](#part-d-back-up-the-mailbox)). Do it before the business email end date.

If nothing arrives:

- Check that the destination address is verified (Part 2) and the rule shows **Active** (Part 3).
- Check the DNS records (Part 4). Wait up to 24 hours after Part 1 [S40].
- Have your helper check on the **DNS Records** page that no Google MX record (`aspmx.l.google.com`, `alt1` to `alt4`) is left. Email Routing does not work together with the MX records of another mail server [S76].
- Cloudflare keeps an **Activity log** for Email Routing. It marks each message as **Forwarded**, **Dropped**, **Rejected**, **Delivery failed** or **Error** [S79]. The help page does not give the clicks to reach it. Look for "Activity log" inside **Email Routing** and show the line to your helper.

### Limits of the forwarding

- Replies come from Gmail. Email Routing cannot send or reply as info@hairbygerta.com. Your reply goes out from your Gmail address, and the client sees that address [S80]. Sign your replies with the salon name.
- No failure notice. If a forwarded message does not reach your Gmail, the sender is not told [S80]. Repeat the test in Part 5 from time to time.
- Size. A message larger than 25 MiB (a little over 25 megabytes) is rejected [S81].
- Sender checks. Cloudflare rejects mail that fails both of its sender checks (SPF and DKIM) and mail from senders on spam block lists [S80].
- One destination. Each routing rule forwards to one destination address [S81].
- Keep your Gmail address in Cloudflare. Deleting a destination address disables every rule that uses it [S75]. If you change Gmail address, repeat Part 2 with the new one. Then open **Routing Rules**, select **Edit** on the rule and choose the new destination [S75].
- It works only while the domain's DNS is at Cloudflare [S40].

### For your helper

On 12 October 2026 public DNS showed five Google MX records on hairbygerta.com (`aspmx.l.google.com` and `alt1` to `alt4`) and the TXT record `v=spf1 include:_spf.google.com ~all` [S77]. Section 3, Part A, step 10 copies these records to Cloudflare, so they will be there when you reach this section:

- MX: Email Routing requires Cloudflare's MX records. Existing ones have to be removed or updated [S76]. Cloudflare's help does not show what the **Onboard Domain** screen does about them. If it does not remove them, delete the Google MX records under **DNS** > **Records**, then repeat Part 1.
- SPF: a domain may have only one TXT record that starts with `v=spf1` [S78]. Cloudflare says to merge an existing SPF record with its own into one record. While the business email still sends mail, that record is `v=spf1 include:_spf.mx.cloudflare.net include:_spf.google.com ~all` [S76] [S78].
- If Cloudflare has added its own SPF record next to the Google one: delete the Google one under **DNS** > **Records**. Then go to **Email Routing**, select the domain, open **Settings**, select **Unlock** on the SPF record and edit it to the merged form [S76].
- Only if you are unsure which SPF record to keep: delete every TXT record that starts with `v=spf1` on the bare domain and onboard again. Cloudflare then adds its own record back [S78]. Unlock and merge it as above.
- To switch forwarding off: **Email Routing**, select the domain, **Settings**, **Disable Email Routing**, then confirm. This removes the MX, SPF and DKIM records that Cloudflare added [S76]. Before that, select **Unlock** on the records and add the other mail provider's records, so no mail is lost [S76].
- To send mail back to the business email, the other provider's records are the five Google MX records named above. They are also in the export from [Section 4, Part 1](#part-1-save-a-copy-of-todays-dns-records), if it was made before forwarding was turned on. This only helps while the business email is still paid [S31].

## 6. How to replace a placeholder with a real photo

A placeholder is a beige picture with a faint logo. It holds the spot of a photo that could not move with you from Wix. This section shows how to put your own photo in such a spot and publish it. Start with one spot. If the computer steps are new to you, do them together with your helper.

Publishing goes through the GitHub account achooStorm, which belongs to your helper. So Gerta cannot publish a photo alone. She chooses the photos and can do Parts B to D. Part E is done by the helper, or by the two together on a computer where the helper has signed in.

You need the computer that has the folder `hairbygerta`. It also needs Python (the free program that builds the pages) and GitHub Desktop (GitHub's free program for sending changes to GitHub). The steps are written for Windows. The new site must already be published ([Section 1, Part 5](#part-5-your-helper-publishes-the-new-site-the-first-time)).

Words used in this section:

- **Repository**: the project on GitHub that holds the site files. It also keeps the history of every file [S63].
- **Commit**: a saved set of changes with a short note about what changed [S82].
- **Push**: send your commits to GitHub [S83].
- **Alt text**: a short description of a photo. It is read aloud to people who cannot see the photo.
- **px**: pixels, the dots a picture is made of.

### Which photos you may use

Use only a photo that passes the test in [Section 1, Part 2](#part-2-collect-your-own-photos): you took it yourself, or you have written permission for it, or you bought it yourself outside Wix with a license for website use.

Never use any of the 26 photos from the old Wix site. That means no file from the folder `hairbygerta-wix-only-photos`, no screenshot of the old site and no picture saved from it. Wix allows the Shutterstock photos bought through Wix only on Wix [S4]. Its free photos and template photos are for use within Wix only [S5].

Decide before you publish. The site is public [S3]. A photo that you take off again later still stays in the history of the repository [S84].

### Set up GitHub Desktop (first time only)

Skip this part if GitHub Desktop is already on the computer and shows the repository hairbygerta.

1. Go to https://desktop.github.com/ and click **Download for Windows** [S85].
2. In the Downloads folder, double-click the GitHub Desktop setup file [S85]. GitHub Desktop opens when the installation is complete [S85].
3. Look at what GitHub Desktop shows. The first time it starts, it shows the screen "Welcome to GitHub Desktop" and no menus [S86]. If you see that screen, click **Sign in to GitHub.com** there and go on with step 7.
4. If you see the normal window with menus instead, open the **File** menu and click **Options** [S87].
5. On the **Accounts** pane, click the "Sign Into" button for GitHub.com [S87].
6. Click **Continue With Browser** [S87].
7. In the browser, **your helper signs in** to their GitHub account achooStorm with their own password and, if GitHub asks for it, their two-factor code (a second sign-in code) [S87]. Nobody else types that password.
8. Follow the prompts to return to GitHub Desktop [S87]. If it now asks for a name and an email address, read step 10 before you answer.
9. Open the **File** menu and click **Options**. In the "Options" window, click **Git** [S88].
10. Check the name and the email address shown there. Both are saved with every commit, and anyone can see them, because the repository is public [S88]. Choose the ones you are willing to show, then click **Save** [S88].
11. In the menu bar, select **File**, then click **Add local repository** [S89].
12. Click **Choose...** and pick the folder `hairbygerta` [S89].
13. Click **Add repository** [S89].

Use the `hairbygerta` folder that the site was published from. On a computer that does not have that folder, open the **File** menu and click **Clone Repository** instead. That makes a copy of the repository on the computer [S90].

A cloned folder has no guard against Wix-only photos yet. The guard is a check that runs with every commit, but only where it was switched on [S82]. Your helper switches it on with one command, once after the repository is created (Section 1, Part 5 does that) and once after every clone: type `python tools/licensing_check.py --install-hook` in the black window (Command Prompt) opened in the folder. Do not copy the guard file by hand. Until then, type `python tools/licensing_check.py` there before Part E, and go on only when it answers `Photo licensing check passed`.

### The steps, shown with one example

The example puts your photo in the fifth spot of the Gallery page. The file name of that spot is `g05`. For another spot, use its name wherever the steps say `g05`. The table after the steps lists every name.

#### Part A: Get the latest version

1. Open GitHub Desktop.
2. Click **Fetch origin**. This checks GitHub for changes that are not in your folder yet [S91].
3. If **Pull origin** shows now, click it. This brings those changes into your folder [S91].

#### Part B: Save your photo twice

4. Open the folder `hairbygerta`, then `images`, and look at `g05.jpg`. It is a wide picture, 1600 x 1066 px.
5. Pick a photo of yours for this spot. A wide spot needs a wide photo, a tall spot a tall one.
6. Open your photo in any photo program.
7. Crop it to about the shape of the placeholder.
8. With the Resize or Export option, save a copy as a JPG file, 1600 px on its long side. Name it `g05.jpg` and save it in `hairbygerta/images`.
9. Say yes when the computer asks whether to replace the file.
10. Save a second copy as a JPG file, 800 px on its long side. Name it `g05.jpg` too and save it in `hairbygerta/images/sm`.
11. Say yes again.

Check these five things:

- Both files are replaced, `images/g05.jpg` and `images/sm/g05.jpg`. One of the two is not enough.
- Both files have exactly the placeholder's name, in small letters, ending in `.jpg`.
- The large one is in `images`. The small one is in `images/sm`.
- A photo that is smaller than 1600 px stays as it is. Do not enlarge it.
- A phone photo can carry the place where it was taken. To remove it, right-click the file and choose **Properties**. On the **Details** tab click **Remove Properties and Personal Information**. Select **Remove the following properties from this file**, click **Select All**, then **OK**. Do this for both files.

#### Part C: Tell the site about the photo

12. Open the folder `hairbygerta`, then `tools`.
13. Right-click `build_pages.py`, choose **Open with**, then **Notepad**.
14. Near the top, find the list named `PLACEHOLDERS`.
15. Delete the name `g05` from that list. If the name stands in quotation marks, delete them and the comma after it too. Change nothing else.
16. Press Ctrl + S to save. Close Notepad.
17. Open the folder `hairbygerta`, then `content`.
18. Open `gallery.json` in Notepad the same way.
19. Find `"file": "g05"`.
20. Right after it, on the same line or the next one, find `"alt": ""`. Type a short description of your photo between the two quotation marks. Example: `"alt": "Layered bob haircut seen from the side"`.
21. Press Ctrl + S to save. Close Notepad.

About the description: say what the photo shows, in a few words. Do not start with "Photo of". Do not use the " character inside it. Leave `alt_original` alone. It describes the old Wix photo.

#### Part D: Build the pages and look

22. Open the black Command Prompt window in the folder `hairbygerta`. Steps 1 to 3 of [Section 1, Part 1](#part-1-look-at-the-new-site) show how.
23. Type `python tools/build_pages.py` and press Enter. This writes the pages again. Read what it prints. A line that starts with WARNING names a step that was forgotten and says how to fix it. Fix it and do step 23 again, until no line starts with WARNING or ERROR and the last line reads `10 pages built.`
24. Type `python -m http.server 8000 --bind 127.0.0.1` and press Enter. This starts the same preview on your own computer as in Section 1, Part 1.
25. Open your web browser and go to `http://localhost:8000/gallery/`.
26. Look at the fifth photo. It must be your photo, sharp and not stretched.
27. Click the photo. The large copy opens.
28. Close the black window. This stops the preview.

If you still see the beige box, hold Ctrl and Shift and press R. That loads the page fresh, without the copy the browser kept [S92] [S93].

#### Part E: Publish

29. Open GitHub Desktop. The **Changes** tab on the left lists every file that changed [S82].
30. Check the list. For this example it holds these six files: `images/g05.jpg`, `images/sm/g05.jpg`, `tools/build_pages.py`, `content/gallery.json`, `gallery/index.html` and `image-manifest.json`. The last one is the site's list of all pictures. The build in step 23 wrote your photo into it by itself, with the status `owner-photo`. Never edit that file by hand. If one of the six is missing, a step of Part B or Part C was skipped. Go back to step 23 and read its lines.
31. In the **Summary** field, type a short note, for example `Real photo for g05` [S82].
32. Under the Description field, click the button that starts with **Commit** and ends with **to main**. GitHub's help page calls it **Commit to BRANCH** [S82]. The program puts the number of files into the name, so for this example it reads **Commit 6 files to main** [S86].
33. Click **Push origin** [S82]. This sends the commit to GitHub [S83]. GitHub then publishes the change to the site by itself [S94].
34. Wait up to 10 minutes [S3].
35. Open https://achoostorm.github.io/hairbygerta/gallery/ and check the photo. Once the domain points to the new site, use https://www.hairbygerta.com/gallery/. Hold Ctrl and Shift and press R if you still see the beige box.

If the list in step 30 shows more files, look at each one before you commit. Other `index.html` files and `404.html` that the build wrote again are fine. After New Year all ten change once, because the build puts the year into the footer of every page. A picture or a zip file that you did not put there yourself is not fine. Take it out of the folder first.

For several photos, do Parts B and C for each one. Then do Parts D and E once.

For your helper: the full test of the site is `qa/run_all.py`. Its first lines say how to start it. A run takes about two minutes. After a photo is replaced, its part `qa/licensing_check.py` lists the photo in the class `owner-photo`, so that a person can look at each one. A file that is an exact copy of a Wix-only photo stays a `LICENSING MATCH`, whatever `image-manifest.json` says. Exit code 2 means a licensing match: do not commit.

### Which name is used where

A name can be used on more than one page. Do steps 17 to 21 in every content file listed for the name. Look at every one of those pages in Part D.

| File names | Content files (in `hairbygerta/content`) |
|---|---|
| `g01` `g02` `g04` `g05` `g06` `g07` `g15` `g20` `g21` | `gallery.json` |
| `g14` `g16` `g17` `g18` `g19` | `gallery.json`, `book-online.json` |
| `g10` | `gallery.json`, `book-online.json`, `about.json` |
| `brunette-balayage` `copper-waves` | `gallery.json`, `about.json` |
| `foils-highlights` `makeup-red-lips` | `home.json`, `gallery.json`, `book-online.json` |
| `home-styling` `home-smile` `home-waves` `meet-extensions` | `home.json` |
| `about-salon` | `about.json` |
| `svc-haircut` `svc-bridal` | `book-online.json` |

`home.json` is the Home page, `gallery.json` the Gallery page, `book-online.json` the Book Online page and `about.json` the About page. Outside the Gallery, the page cuts the photo to the shape of its spot, so keep the hair or the face near the middle.

On the Home page every spot is tall, whatever shape the placeholder file has. The four photos in the row are shown about 288 x 545 px, the small Meet Gerta photo about 313 x 422 px and the large one about 424 x 637 px. For `home-styling`, `home-smile`, `home-waves` and `meet-extensions`, crop your photo to a tall shape like that in step 7, not to the shape of the placeholder. A wide photo would be cut hard at the sides and look soft there.

The two real photos on the site, `g12` and `g13`, are not in this table, because they are not placeholders. To change one of them, ask your helper: each has two more copies in another file format that have to be changed with it.

To see the size of a placeholder, right-click it, choose **Properties** and open the **Details** tab. The line Dimensions shows it.

### If something goes wrong with a photo

- Step 23 prints a line that starts with WARNING: a step was forgotten, and the line says which one. The name was deleted from the list but a file is still the placeholder picture, or the photo was saved but its name is still in the list, or only one of the two files was replaced, or the description after `"alt"` is still empty. Do what the line says and do step 23 again.
- Step 23 prints a line that starts with ERROR, or shows the word SyntaxError or Traceback: the message names a file. If it is a picture, it is not a JPG file. Save your photo again as JPG under that name. If it is `tools/build_pages.py` or a file in `content`, most likely a quotation mark or a comma got lost in Part C. In GitHub Desktop, right-click that file in the list of changed files and click **Discard changes** [S82] [S86]. In the "Confirm Discard Changes" window, click **Discard Changes** again [S82]. Then do the edit once more.
- GitHub Desktop does not commit and shows `PHOTO LICENSING CHECK: STOP`: the folder has a guard that runs with every commit [S82]. It names a file that must not be published: a file with the same content as one of the 26 Wix-only photos, or a zip file. Save a photo of your own over that file. Or put the placeholder back: right-click the file in the list of changed files and click **Discard changes** [S82] [S86]. Take a file out of the folder only when it is an extra file that the site never had. Then commit again.
- When the guard stops a commit, GitHub Desktop shows the guard's message and offers the button **Commit anyway** [S95]. Never click **Commit anyway** and never choose **Bypass Commit Hooks**. Both commit the file without the check [S82] [S95]. The same holds when the message starts with `PHOTO LICENSING CHECK: COULD NOT RUN` or says that Python 3 was not found: stop and ask your helper.
- The guard only recognises an exact, unchanged copy of a Wix-only file. A Wix photo that was cropped, resized or saved again is not recognised. So a commit that goes through is no proof that a photo may be used. The rule under [Which photos you may use](#which-photos-you-may-use) decides [S4] [S5].
- You want the placeholder back after publishing: in GitHub Desktop click **History** in the left sidebar, right-click your commit and click **Revert Changes in Commit** [S84]. This takes back everything in that commit, so every photo you published with it. If you made other commits after it, ask your helper first: GitHub says to revert from newest to oldest, otherwise you may see merge conflicts (changes that do not fit together) [S84]. Then click **Push origin** [S82]. The photo is off the site, but it stays in the history of the repository [S84].

## 7. How to paste the Square booking link

Today every **Book Now** button on the new site calls 347-671-5095. After these steps every **Book Now** button opens your Square booking page. Gerta brings the booking link (Part A). Your helper pastes it into the site (Part B), because the site is in the helper's GitHub account. Gerta cannot do Part B alone. Use a computer. Together it takes about 15 minutes.

Words used in this section:

- **Booking link**: the web address of your Square booking page. Square's help page calls it the booking flow URL [S15].
- **Tab**: one page inside your browser window.
- **Repository**: the project on GitHub that holds the site files [S63].
- **Commit**: a saved set of changes with a short note about what changed [S82].
- **Branch**: a parallel version of the repository [S96]. The site is published from the branch called main.

Before you start:

- Your Square online booking site must be published. Square gives the link only after that [S15].
- The new site must be published, so that it opens at the preview address https://achoostorm.github.io/hairbygerta/.

### Part A: Have your booking link ready

1. Open the note with your booking link. You copied it in [Section 1, Part 3](#part-3-set-up-square-appointments-on-the-free-plan), steps 32 to 38. If the note is lost, do those steps again. Square's help page links to your Square Dashboard at https://app.squareup.com/dashboard/appointments [S15].
2. Copy the link.
3. Open a new tab.
4. Paste the link into the address bar and press Enter. Your booking page must open. If it does not, get the link again as in step 1.

### Part B: Paste the link into the site

1. **Your helper signs in** to github.com with their account achooStorm. Gerta gives the helper the booking link from Part A. Nobody passes on a password or a sign-in code.
2. Open https://github.com/achooStorm/hairbygerta.
3. Click the folder **js**.
4. Click the file **site.js** [S97].
5. In the upper right corner of the file view, click the pencil icon, **Edit file** [S97].
6. Near the top of the text, find this line:

   `var BOOKING_URL = "";`

7. Click between the two quote marks.
8. Paste the link. The line now looks like this, with your own link in the middle:

   `var BOOKING_URL = "https://your-booking-link";`

9. Check the line. Both quote marks are there. The semicolon (;) is still at the end. There is no space inside the quote marks. The link starts with https://. Change nothing else in the file.
10. Click **Commit changes...** [S97].
11. In the "Commit message" field, type `Add Square booking link` [S97].
12. Below the commit message fields, choose to add the commit to the current branch, not to a new branch [S97].
13. Click **Commit changes** [S97].

About step 12: GitHub's help page suggests a new branch here [S97]. Skip that for this one line. GitHub publishes the site from one branch, and a change on another branch does not reach the website [S94]. If GitHub does not offer the current branch, stop and commit nothing.

GitHub now publishes the change by itself [S94]. It can take up to 10 minutes [S3].

The file js/site.js is now changed on GitHub, but not yet in the `hairbygerta` folder on the computer. Before the next upload from that folder, the helper must pull first. Pull means: fetch GitHub's latest version into the folder [S98]. [Section 6, Part A](#part-a-get-the-latest-version) shows how.

### Part C: Check that it worked

1. Wait 10 minutes [S3].
2. Open the Book Online page of the new site. Until www.hairbygerta.com shows the new site, use https://achoostorm.github.io/hairbygerta/book-online/. After that, use https://www.hairbygerta.com/book-online/.
3. Reload the page so the browser fetches the changed file. On Windows hold Ctrl and Shift and press R [S92] [S93]. On a Mac in Chrome hold Command and Shift and press R [S92]. In Safari on a Mac that key combination opens Reader instead [S99]. There, open the **View** menu and choose **Reload Page**, or hold Command and press R [S100].
4. Click the first **Book Now** button. Your Square booking page must open in a new tab.
5. Close that tab.
6. Repeat steps 4 and 5 for the other nine **Book Now** buttons. There are 10 in all.
7. On your phone, open the same page and tap one **Book Now** button. The booking page must open.

The **Book Online** button on the home page still opens your own Book Online page. That is correct.

If the buttons still call the phone number after an hour [S3], the line most likely has a typing mistake. Open the file again (Part B, steps 2 to 5) and compare the line with step 8, character by character. One wrong character there also switches off the photo viewer in the gallery (each photo then opens on its own) and shows the phone menu as a plain list of links without the menu button, because the same file runs them. The menu links keep working. If you cannot find the mistake, do Part D.

If a **Book Now** button opens a new tab but not your booking page, the link between the quote marks is wrong or not complete. Open the file again (Part B, steps 2 to 5), delete everything between the two quote marks, paste the link from your note again and do Part B, steps 9 to 13.

### Part D: How to go back

1. Do Part B, steps 1 to 5 again.
2. Delete everything between the two quote marks. The line must again be exactly:

   `var BOOKING_URL = "";`

3. Do Part B, steps 10 to 13. As the message type `Remove Square booking link`.
4. Wait 10 minutes [S3], then reload the page as in Part C, step 3.

Empty quote marks mean there is no booking link. Every **Book Now** button calls 347-671-5095 again.

## 8. What cannot be undone

Four things in this move are hard or impossible to undo. Two are final: a domain that was lost after it expired, and a closed Wix account. Two can only be bought again: an ended site plan and an ended mailbox. For the mailbox, Wix names no number of days in which the old mail comes back. For each of the four: what it means for you, and the one thing to do first. The end dates are the ones you wrote down in [Section 2](#write-it-down).

### Part 1: The Wix site plan ends

**What it means for you.** The Wix site is not deleted and keeps its content [S19]. But it leaves hairbygerta.com: its address goes back to a free Wix address, and Wix ads appear on it [S19]. A site plan that has ended cannot be switched back on. You would have to buy a new one [S24]. So from that day the Wix site is your safety net only if you buy a new plan.

A Wix site plan only ends if it was canceled. Otherwise Wix renews it by itself, a yearly plan up to 3 weeks before its expiration date, and it does not refund renewals [S19] [S23]. If you do not want to pay Wix for another period, decide this with your helper more than 3 weeks before the expiration date. Then cancel the plan:

1. **Gerta signs in** to Wix and goes to **Premium Subscriptions** [S19].
2. Click the **More Actions** icon next to the plan [S19].
3. Click **Cancel Plan** [S19].
4. Click **Cancel Now** to confirm [S19].

Canceling does not end the plan at once. The plan stays active until the end of the paid period and then does not renew [S19]. So the Wix site keeps running until the end date, and until then a canceled plan can be switched back on [S24]. One exception: a plan that is canceled in its first 14 days ends immediately [S19].

**The one thing to do first.** At least a week before the site plan's end date, have your helper confirm that hairbygerta.com already shows the new site. The two sites look alike, so do not judge by eye. The checks are in Section 4 under [What you see when it has worked](#what-you-see-when-it-has-worked).

If it does not, you can keep the Wix site as your fallback: before the end date, **Turn Auto Renew On** on the **Premium Subscriptions** page switches a canceled plan back on [S24]. That payment cannot be undone either. Wix may take it up to 3 weeks before the end date and does not refund renewals [S19].

If the domain has already left Wix, that alone does not bring the Wix site back to hairbygerta.com, because Wix disconnects the site when the domain is transferred away [S35]. Then also do the steps under [If something goes wrong: point the domain back to the Wix site](#if-something-goes-wrong-point-the-domain-back-to-the-wix-site) in Section 3.

### Part 2: The domain expires

The domain is the address hairbygerta.com. It has its own end date, separate from the site plan [S19]. The registry (the organization that keeps the official list of all .com addresses) showed that it expires on 27 November 2026 at 01:04 UTC when read on 13 October 2026 [S27]. In New York that is the evening of 26 November 2026, so treat 25 November 2026 as the last safe day. Your **Domains** page in Wix shows the expiry date too [S25].

**What it means for you.** An expired domain is no longer connected to your site [S101]. ICANN (the organization that sets the rules for domain names) says its website and email get cut off for a time, as a last warning [S102]. That hits the new site and info@hairbygerta.com as well.

How long you can still renew, by Wix's own pages:

- **About the first 30 days (the Grace Period).** Renew at no extra fee: on the **Domains** page, click **Extend Registration** in the banner under the domain [S101]. Nobody else can register the name. But in the last 10 days the company Wix resells domains from may auction it privately [S101]. So only about 20 days are safe.
- **About 30 days more (the Redemption Period).** A last chance: click **Keep Domain** in the banner under the domain and pay a fee [S101]. Wix says this is not guaranteed and can take up to 7 days [S101]. One Wix page says the fee varies and is shown on your **Domains** page [S101]. Two others say \$100 [S103] [S104]. The domain can no longer be moved to another company [S104]. ICANN's rule matches: 30 days, and a fee is allowed [S102].
- **After that (Pending Delete).** You cannot get it back. 5 to 10 days later anyone can buy it, and you have no claim to it [S101].

If someone else buys the name, every link, Google result and business card with hairbygerta.com leads to them.

**The one thing to do first.** Before the expiry date, make sure the domain is either renewed at Wix or has completely finished moving to its new registrar (the company where a domain is registered and renewed).

Not sure the move will finish in time? Then renew the domain at Wix for one more year. This is a payment that only Gerta decides on, and Wix does not refund domain payments [S45]. With auto renew on (Wix charges your card by itself), Wix takes the payment 30 days before the expiry date [S26]. If the registry date is right, that is around 27 October 2026. With auto renew off, renew by hand:

1. **Gerta signs in** to Wix and goes to **Domains** [S105].
2. Click **Extend** next to hairbygerta.com [S105].
3. Choose one year and click **Continue** [S105].
4. Select a privacy option and click **Continue** [S105]. Each option shows its own price. If you choose the one with DNSSEC, Section 3, Part B turns it off again before a move.
5. Enter your payment information and click **Submit Purchase** [S105].

Change nothing in the contact details while you do this. Wix says that would lock the domain from transfer for 60 days [S104]. Either way, open the **Domains** page afterwards and check that the expiry date now says 2027. If a renewal payment fails, the domain still expires on the old date [S103]. Both ways, with and without the renewal, are in Section 3 under [Check your dates first](#check-your-dates-first).

### Part 3: The business email ends

The business email is the mailbox info@hairbygerta.com, which Wix sells as a Google Workspace business email [S31].

**What it means for you.** After it expires you can no longer read, receive or send mail from it [S31]. Wix says the old mail is kept only as long as Google's rules allow, and comes back only if you buy the mailbox again within that time. Wix gives no number of days [S31]. Google's page for people who buy from Google directly says the data is deleted after a cancellation and cannot be restored [S106]. So count on the old mail being gone on the end date.

**The one thing to do first.** Download a copy of the whole mailbox with Google Takeout, Google's tool for downloading your data [S32]. The steps are in [Section 2, Part D](#part-d-back-up-the-mailbox).

Do it now, and one last time later, as Section 2, Part D says. A copy only holds the mail that was there when you asked for it [S32].

The mailbox only ends if you cancel it. Otherwise Wix tries to take the renewal payment up to 30 days before the expiration date, and a business email bought through Wix is not refunded [S30]. If you do not want to pay for another period, decide with your helper and cancel before the date in the **Upcoming payment** column. Make the first backup before you cancel.

1. **Gerta signs in** to Wix and goes to **Premium Subscriptions** [S30].
2. Click the **More Actions** icon next to the business email [S30].
3. Click **Cancel subscription** [S30].
4. Read the screen and follow it to the end. Wix's two help pages name the last clicks differently, so go by what the screen says [S30] [S59].

The mailbox is not canceled at once. It keeps working until the end of the paid period [S30]. Until then you can switch it back on: click the **More Actions** icon next to it, then **Turn auto renew on** [S30].

New mail is a separate matter. After the end date the mailbox no longer receives mail [S31]. From then on, mail for info@hairbygerta.com only reaches you if the forwarding in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) is on.

### Part 4: The 14 Shutterstock photos

**What it means for you.** You bought these 14 photos inside Wix. Wix's rules: they cannot be downloaded, and they may be used only on Wix, not with other website services [S4]. So they can never move to the new site. They stay usable on any site in the same Wix account [S4]. On the new site a placeholder (a beige box with a faint logo) stands in for each one.

The same goes for 12 more photos from the old site. Eleven came free with Wix or its template, and Wix allows those within Wix only [S5]. For one there is no proof of a license (the permission that says where a photo may be used). That makes 26 placeholders.

The step with no way back is closing the Wix account: you lose access to the account and everything in it [S107].

**The one thing to do first.** Never close the Wix account while hairbygerta.com is still registered at Wix, while the business email is still in use, or while you may still need the Wix site. Closing cannot be undone, and you lose access to everything in the account [S107]. Wix lets you close it as soon as auto renew is off, without waiting for the domain or the plans to end [S19] [S107]. So close it only after the domain has completely finished moving to its new registrar, the mailbox is backed up and the forwarding works, and you are sure you will never want the Wix site or those photos again. There is no hurry: the account can stay open for free once the paid subscriptions are canceled [S107].

For the new site, use photos of your own: see [Section 1, Part 2](#part-2-collect-your-own-photos). Never save or screenshot a photo from the Wix site.

## 9. Yearly cost after the move

Prices change, so read each price again on the day you pay.

After the move you pay one bill a year: the domain (the address hairbygerta.com). Everything else runs on a free plan.

| What | Where | Cost per year |
|---|---|---|
| Domain hairbygerta.com | Cloudflare Registrar | \$10.46 at the price shown on 12 October 2026 [S44] |
| Website | GitHub Pages | \$0 [S2] [S108] |
| Domain settings (DNS) | Cloudflare, Free plan | \$0 [S109] |
| Email forwarding for info@hairbygerta.com | Cloudflare Email Routing | \$0 [S73] |
| Online booking | Square, plan Square Free | \$0 [S7] |
| **Total** | | **\$10.46 a year at today's price, before any sales tax** |

Not in the total:

- Sales tax. Cloudflare collects sales tax based on the billing address in your Cloudflare account [S110]. So the amount on the payment screen and on the invoice can be a little higher than the price in the search.
- Square's fee on each card payment. See [Square](#square-free-plan-fees-only-on-payments) below.
- The one-time cost of moving the domain. See [The rules today](#the-rules-today) in Section 3.
- If you stop after the first move, the domain line is the renewal price of the in-between registrar instead. Read it on its website.
- If you and your helper decide to leave the domain registered at Wix, the domain line is Wix's renewal price instead, and the two Cloudflare lines fall away. The domain's settings then stay at Wix [S37], and the free email forwarding only works with the settings at Cloudflare [S40]. To keep info@hairbygerta.com you would go on paying Wix for the business email. Look both prices up as shown under [What you pay Wix today](#what-you-pay-wix-today-look-it-up).

### The domain: the one bill

- A registrar is the company where a domain is registered and renewed. Cloudflare Registrar charges only what the registry (the organization that keeps the official list of all .com addresses) and ICANN (the organization that sets the rules for domain names) charge it, with no markup [S44].
- On 12 October 2026 Cloudflare's domain search showed a .com name at \$10.46, with the line **Renews at \$10.46/year** [S44].
- Cloudflare's price list also says "Starting at \$7.85" for its registrar, but names no domain ending [S109]. Go by the search page.
- Cloudflare renews at the list price set by the registry [S111]. So the price can change from one year to the next.
- Auto renew means Cloudflare charges your payment method by itself. It is on by default, and the first try comes about 30 days before the domain expires [S111].
- Auto renew can fail, for example when the card on file has expired. Cloudflare then emails you and tries three more times. If those tries fail too, you must renew by hand: go to **Manage domains**, select **Manage** next to the domain, select **Renew/Extend Domain**, then **Renew** and **Purchase** [S111].
- A domain that is not renewed before its expiry date goes into a Redemption Grace Period of 30 days. It can be restored, but that may cost an extra fee, and it cannot be transferred during that time [S111].
- Cloudflare sends two monthly emails: one lists the domains expiring in the next 60 to 90 days, the other lists the domains set to renew automatically within the next 45 days [S111]. The page does not say that the second one comes before the first charge. It names the receiver the Super Admin of the domain [S111]. If these emails do not reach the address Gerta uses to sign in to Cloudflare, ask your helper to check who has that role in the account.
- The contact email address of the domain also gets warnings: every week in the last month before the expiry date and every day in the last seven days [S111].
- Renewals are final. Cloudflare gives no refund [S111].

So once a year, check that the payment method in Cloudflare is still valid. After the renewal, check that the domain shows its new expiry date.

Check the price before you pay for the transfer, and again each year when the 60 to 90 day email comes:

1. Go to https://www.cloudflare.com/domains/ [S44].
2. Click the box **Search for a domain name** [S44].
3. Type a made-up name that ends in .com, for example your first name with today's date. Typing hairbygerta.com shows **Unavailable** and no price, because that name is taken [S44].
4. Read the price at the right end of the .com result and the **Renews at** line under it [S44]. Keep the mouse pointer off the result. While the pointer is on it, the price is replaced by the words **Buy now**. Move the pointer away and the price comes back [S44].
5. Close the page. Do not click a result or its price: the price itself is the **Buy now** button [S44].

Cloudflare says it shows registration, transfer and renewal prices upfront [S44]. So also read the amount on the Cloudflare screen before you confirm a payment.

### GitHub Pages: free

- Hosting means keeping the site's files on a computer that shows them to visitors. GitHub Pages does this for a public repository (a project on GitHub that anyone can view) on the GitHub Free plan [S108]. GitHub Free costs \$0 [S2].
- GitHub Pages supports using your own domain [S70].
- Limits: a site may be no larger than 1 GB, and there is a soft limit of 100 GB of data sent to visitors per month [S108]. The `hairbygerta` folder is a few megabytes.
- One thing to know. GitHub says Pages may not be used as free hosting to run an online business or an online shop, or for a site that is mainly there to handle sales [S108]. The new site only shows information. It sells nothing and takes no payment: clients book through Square or by phone. The page does not say how GitHub judges a small information site like this one. If GitHub ever writes about it, the message goes to your helper, because the GitHub account is theirs. Ask your helper to tell you at once. Moving the folder to another host could then add a cost.

### Cloudflare DNS and email forwarding: free

- DNS records are the list of settings that tells the internet where the website is and where the email goes. Cloudflare's Free plan costs \$0 a month and includes DNS [S109].
- Email Routing forwards mail for info@hairbygerta.com to your Gmail (Section 5). Cloudflare offers it as free email forwarding, and its pricing page lists incoming email as Unlimited on the free plan [S73] [S74].
- You add a card to Cloudflare only to pay for the domain. If a screen asks you to choose or start any paid plan (for example Pro, Business or Workers Paid), stop and ask your helper [S74] [S109].

### Square: free plan, fees only on payments

- The free plan is called **Square Free**. It costs \$0 a month per location (one place of business) [S7].
- It includes: an online booking website, a Book Now button for your own website, Instagram, Facebook and Google Business Profile, unlimited staff calendars, custom scheduling, automatic text and email appointment reminders, prepayments and appointment deposits [S7].
- It does not include: a cancellation policy with no-show fees, a waitlist, Google Calendar sync, appointment confirmations, or processing time (clients booking during the waiting time of a color service). Those are in Square Plus, which costs \$49 a month per location [S7].
- Square says Square Free has no monthly subscription cost. You pay processing fees only when you take a payment [S7]. A processing fee is the part of a card payment that Square keeps. It is taken out of each payment [S112].
- Fees on Square Free today: 2.6% + 15 cents for a card tapped, dipped or swiped in person, 3.3% + 30 cents for a payment online, 3.5% + 15 cents for a card typed in by hand or kept on file. Cash or check is free [S7].
- Example: a client pays \$100 by card in the salon. Square keeps \$2.75 and you get \$97.25.
- How to sign up without starting a paid trial by mistake is in [Section 1, Part 3](#part-3-set-up-square-appointments-on-the-free-plan), step 2.

### What you pay Wix today: look it up

This guide does not know what Wix charges you. Find it yourself. You only look and change nothing.

1. **Gerta signs in** to Wix.
2. Go to the **Billing History** page: https://www.wix.com/account/billing-history [S113]
3. Use the **All Dates** drop-down to find the charges of the last 12 months [S114].
4. Click the **More Actions** icon next to a charge [S113].
5. Click **View Invoice** [S113].
6. Write down the total and what it was for.
7. Do steps 4 to 6 for every charge of the last 12 months.
8. Add the totals up.

The Billing History page holds the invoices for everything you paid Wix [S114]. Look for the site plan, the domain and the business email. Two services with the same renewal date can share one invoice [S114]. If you paid for more than one year at once, look further back and divide that charge by the number of years.

Your saving each year is that sum minus the total in the table above.

## Official help pages used

Every page in this list was opened on 12 or 13 October 2026. Each entry gives the page title, its address and what it confirms. The numbers follow the order in which the pages are first used in this guide, except [S115] and [S116], which were added last for Section 1, Part 5. Entries marked as a public record are lookups of the domain's own data, not help pages. One entry is the program text of GitHub Desktop, for three things that no help page shows. A few entries are help pages of Google, Microsoft and Apple, for Google Takeout and for the reload keys of their browsers.

- [S1] GitHub Docs, "What is GitHub Pages?". https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages Confirms: the address form of a project site: `http(s)://<owner>.github.io/<repositoryname>`.
- [S2] GitHub, "Plans & pricing for every developer and team". https://github.com/pricing Confirms: the Free plan costs \$0 per user per month.
- [S3] GitHub Docs, "Creating a GitHub Pages site". https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site Confirms: GitHub Pages sites are publicly available on the internet; a change can take up to 10 minutes to publish after it is pushed; GitHub's own next check point is after an hour; with GitHub Free the repository of the site must be public; Visit site under "GitHub Pages"; a site published from a branch needs a push by someone with admin permissions and a verified email address.
- [S4] Wix Help Center, "Using Shutterstock Media Purchased Through Wix". https://support.wix.com/en/article/using-shutterstock-media-purchased-through-wix Confirms: Shutterstock files bought through Wix are not downloadable; they may only be used in websites and content on Wix, not with other website or content services; they are usable on any site in the same Wix account.
- [S5] Wix Help Center, "Wix Media: Adding Free Media from Wix". https://support.wix.com/en/article/wix-media-adding-free-media-from-wix Confirms: the free Wix media in the Media Manager and on the template is for digital use within Wix only.
- [S6] Wix Help Center, "Avoiding Copyright Infringement: Images". https://support.wix.com/en/article/avoiding-copyright-infringement-images Confirms: free Wix images may not be used anywhere outside Wix; for a stock image you bought, check which license you purchased and its restrictions.
- [S7] Square, "Appointments Pricing & Plans". https://squareup.com/us/en/appointments/pricing Confirms: the plan names and prices (Square Free \$0/mo. per location, Square Plus \$49, Square Premium \$149); the buttons Get started and Try free for 30 days; the features included in and missing from Square Free, among them the online booking site; the processing fees; no monthly subscription cost on Square Free, fees only when you take a payment; the customer support phone number; phone support hours per plan (Square Free: 6am to 6pm PT, Monday to Friday, for the first 90 days), with chat support and email support ticked for all three plans.
- [S8] Square Support Center, "Switch to the new Square subscription plans". https://squareup.com/help/us/en/article/8569-switch-to-the-new-square-subscription-plans Confirms: advanced capabilities may already be activated based on business type, and may otherwise have to be added.
- [S9] Square Support Center, "Set up your health & beauty business with Square". https://squareup.com/help/us/en/article/5354-square-appointments-guide Confirms: the setup order, and that step 1 is identity verification and linking a bank account with account and routing numbers.
- [S10] Square Support Center, "Create and manage multiple locations". https://squareup.com/help/us/en/article/5580-manage-multiple-locations-with-square Confirms: the first location is made at sign-up, the menu path Account & Settings, My business, Locations, the business hours field and the Save button.
- [S11] Square Support Center, "Add advanced capabilities". https://squareup.com/help/us/en/article/8486-add-advanced-capabilities Confirms: advanced capabilities, Bookings among them, are not visible in Square Dashboard until activated; the steps Add more, select the capability, Add; some of their features need Square Plus or Square Premium.
- [S12] Square Support Center, "Create and manage services". https://squareup.com/help/us/en/article/6487-create-a-service-from-the-square-appointments-app Confirms: the Service library path, the Create service steps (details, description, price type and price, duration, Save), and the Bookable by customers online switch with its offered services; that Square Free accounts need the advanced bookings capabilities added.
- [S13] Square Support Center, "Add and manage bookable team members". https://squareup.com/help/us/en/article/5350-create-staff-member-profiles-for-square-appointments Confirms: the path Staff, Team, Team members, the Appointments tab, Add to appointments, and the booking information (online booking, bookable services, hours of availability).
- [S14] Square Support Center, "Manage bookable staff schedules and availability". https://squareup.com/help/us/en/article/8443-manage-staff-schedules-and-availability-with-square-appointments Confirms: Appointments, Calendar, the clock icon, Recurring schedule, and that you click an appointment on the calendar to change it.
- [S15] Square Support Center, "Set up online booking". https://squareup.com/help/us/en/article/5355-set-up-online-booking-with-square-appointments Confirms: every step from Enable online booking to Publish; the online booking site URL; that the booking site is free and that its bookings sync with the calendar; that Square Free accounts need the advanced bookings capabilities added; the Square Dashboard link; the steps under "Get your booking flow URL" (Appointments or Payments then Appointments, Online Booking, Channels, "Add your booking flow to an existing site", Get Started, Get URL, location, booking type, copy the booking flow URL, X, Done); that the link is available once the online booking site is published; that Create button and Get embed code give HTML code. The page does not list the booking type choices.
- [S16] Square Support Center, "Manage appointment booking notifications and reminders". https://squareup.com/help/us/en/article/6729-customer-confirmations-with-square-appointments Confirms: notifications may require specific subscriptions or settings and go out by email or text message.
- [S17] Square Support Center, "Adjust your appointment settings". https://squareup.com/help/us/en/article/5351-manage-your-square-appointments-account-settings Confirms: the Settings pages Calendar & booking (Reservation Guarantee) and Communications; the path Appointments (or Payments, Appointments), Settings, History to past appointments; and the steps More, Cancel Appointment on the Appointment Details page.
- [S18] Square Support Center, "Accept or decline appointments". https://squareup.com/help/us/en/article/8444-accept-or-decline-appointments Confirms: a pending appointment appears on the calendar; Accept or Decline, then a notification type (email or text) with an optional message, then Send.
- [S19] Wix Help Center, "Canceling a Wix Premium or Studio Plan". https://support.wix.com/en/article/canceling-a-wix-premium-plan Confirms: a canceled plan stays active until the end of the subscription period; after that the site stays online with its content, on the free Wix address and with Wix ads; the expiration date is on the Premium Subscriptions page; a plan may renew up to 3 weeks before its expiration date; no refunds for renewals; domain and business email are not canceled with the plan; the steps More Actions, Cancel Plan, Cancel Now; a plan canceled in its first 14 days ends immediately; once auto renew is off the account can be closed without waiting.
- [S20] Wix Help Center, "Business Email: An Overview". https://support.wix.com/en/article/business-email-an-overview Confirms: Wix business email is Google Workspace; the Business Email page (manage.wix.com/account/mailboxes) shows the business emails you own.
- [S21] Wix Help Center, "Viewing Your Site Plans and Other Subscriptions". https://support.wix.com/en/article/viewing-your-premium-plans Confirms: plans and other Wix purchases are listed on the Premium Subscriptions page; the View Subscriptions link; the wrong-account note and the account email locator.
- [S22] Wix Help Center, "Checking Your Upcoming Renewals for Premium or Studio Plans". https://support.wix.com/en/article/checking-your-upcoming-renewals-for-premium-plans Confirms: plans renew automatically at the end of the subscription period; the Upcoming payment column shows the date of the next renewal payment; the Info icon; the date can differ from the expiration date when auto renew is off.
- [S23] Wix Help Center, "Wix Billing for Site Plans". https://support.wix.com/en/article/wix-billing-for-premium-plans Confirms: where to see the site plan's next payment; yearly plans renew up to 3 weeks before expiry; domains and business emails are charged 30 days before the expiration date.
- [S24] Wix Help Center, "Reactivating a Canceled Premium or Studio Site Plan". https://support.wix.com/en/article/reactivating-a-canceled-premium-plan Confirms: Turn Auto Renew On on the Premium Subscriptions page reactivates a canceled plan before it ends; after it has ended you have to buy a new plan.
- [S25] Wix Help Center, "Accessing Your Domains Page". https://support.wix.com/en/article/accessing-your-domains-page Confirms: user panel, Account Settings, Domains; the Assigned Domains section; the Domains page shows the expiry and payment renewal dates.
- [S26] Wix Help Center, "Checking Your Domain Subscription Renewal Date". https://support.wix.com/en/article/checking-your-domain-subscription-renewal-date Confirms: the Premium Subscriptions page and its Upcoming payment column for the domain; domains bought from Wix renew automatically 30 days before their expiration date.
- [S27] Verisign (the .com registry), public registration record for hairbygerta.com. https://rdap.verisign.com/com/v1/domain/hairbygerta.com Confirms: a public record, not a help page. Read on 12 and on 13 October 2026: registrar Wix.com Ltd., registered 27 November 2025, expires 27 November 2026 at 01:04:09 UTC; also the lock status, the nameservers and the DNSSEC setting on those days.
- [S28] ICANN, "ICANN Lookup" (registration data lookup tool). https://lookup.icann.org Confirms: a page where anyone can look up the current registration record of a domain name. The lookup was not run there for this guide; the record was read at the registry [S27].
- [S29] Wix Help Center, "Google Workspace: Checking Your Business Email Subscription Renewal Date". https://support.wix.com/en/article/google-workspace-checking-your-business-email-subscription-renewal-date Confirms: the Upcoming payment column for the business email; the Info icon; the date can differ from the expiration date when auto renew is off.
- [S30] Wix Help Center, "Google Workspace: Canceling Your Business Email Renewal". https://support.wix.com/en/article/google-workspace-canceling-your-business-email-renewal Confirms: renewal payments are attempted up to 30 days before the expiration date; a canceled business email works until the end of the paid period; the steps More Actions, Cancel subscription and what follows; Turn auto renew on; business emails bought through Wix are not refunded. The page has no steps for exporting mail.
- [S31] Wix Help Center, "Google Workspace: Availability of Business Email Data Following Cancellation". https://support.wix.com/en/article/google-workspace-availability-of-business-email-data-following-cancellation Confirms: after the paid period ends you can no longer read, receive or send email from the business mailbox; the data is kept under Google's retention rules and restored only if the business email is repurchased within that period; no number of days is given. The same article also opens under an older address that ends in availability-of-google-workspace-formerly-g-suite-mailbox-data-following-cancelation; the page has no steps for exporting mail.
- [S32] Google Account Help, "How to download your Google data". https://support.google.com/accounts/answer/3024190 Confirms: Google Takeout (takeout.google.com) exports and downloads your data, email included; its steps and option names; the waiting time; the 7 day expiry and the 5 download limit; changes made after the request may not be in the file.
- [S33] Wix Help Center, "Google Workspace: Accessing your Business Email Through Your Wix Account". https://support.wix.com/en/article/google-workspace-accessing-your-business-email-through-your-wix-account Confirms: sign in at Gmail.com with the full business address; switch Google account with the profile image or initial at the top right; the page has no steps for exporting mail.
- [S34] Google Workspace Admin Help, "Allow or block Google Takeout". https://knowledge.workspace.google.com/admin/users/advanced/allow-or-block-google-takeout Confirms: Takeout is allowed by default for Google Workspace and an administrator can change that (Admin console: Menu, Data, Data import & export, Google Takeout).
- [S35] Wix Help Center, "Transferring Your Wix Domain Away from Wix". https://support.wix.com/en/article/transferring-your-wix-domain-away-from-wix-2477749 Confirms: the transfer steps and button names; the code goes to the registrant contact email; usually up to 7 days; the Wix site is disconnected and MX records must be added again; who may transfer; privacy advice; the Whois Lookup status; the Grace Period.
- [S36] Cloudflare Docs, "Transfer your domain to Cloudflare" (last updated Apr 24, 2026). https://developers.cloudflare.com/registrar/get-started/transfer-domain-to-cloudflare/ Confirms: the domain must be active in Cloudflare first; no direct transfer from Wix and the two-move route; 60-day rules; DNSSEC off and the 24 hour wait; codes expire; Transfer domains and Confirm transfer; approval and the five days; up to 10 days; at cost and one year added per transfer; the contact information must be accurate and is kept out of public WHOIS by default; selecting Confirm transfer agrees to the domain registration terms; after a renewal, wait at least 45 days after the original expiration date.
- [S37] Wix Help Center, "Request: Changing Name Server (NS) Records for a Wix Domain". https://support.wix.com/en/article/request-changing-name-server-ns-records-for-a-wix-domain Confirms: the nameservers of a Wix domain cannot be changed.
- [S38] Wix Help Center, "ICANN's 60 Day Lock Policy". https://support.wix.com/en/article/icanns-60-day-lock-policy Confirms: Wix applies 60 days after registration, a contact change or a transfer; a locked domain can stay at Wix and be pointed to an external site; the advice to transfer before changing contact information.
- [S39] Wix Help Center, "Connecting a Wix Domain to an External Site". https://support.wix.com/en/article/connecting-a-wix-domain-to-an-external-site Confirms: Manage DNS Records; a Wix domain can point to an outside site by its A and CNAME records; nameservers cannot be changed.
- [S40] Cloudflare Docs, "Route emails". https://developers.cloudflare.com/email-service/get-started/route-emails/ Confirms: Email Routing forwards incoming email to existing mailboxes; Cloudflare DNS is required; Compute, Email Service, Email Routing and its direct link; Onboard Domain, Done; the three kinds of DNS records added; 5 to 15 minutes, up to 24 hours; Destination Addresses and Verify email address; Routing Rules, Create routing rule, Email pattern, Action, Send to an email, Destination, Save; the test steps, sending from a different account, the spam folder.
- [S41] ICANN, "Transfer Policy" (updated 21 February 2024). https://www.icann.org/en/contracted-parties/accredited-registrars/resources/domain-name-transfers/policy Confirms: the 60-day periods; the five calendar days for the old registrar to answer; the five calendar days to give the code and remove the lock.
- [S42] ICANN, "FAQs for Registrants: Transferring Your Domain Name". https://www.icann.org/resources/pages/name-holder-faqs-2017-10-10-en Confirms: the same 60-day rules in plain words; the code within five calendar days; the registrar can be found with ICANN's lookup tool.
- [S43] ICANN GNSO, "PDP Transfer Policy Review" (page last updated 21 April 2026). https://gnso.icann.org/en/group-activities/active/transfer-policy-review Confirms: the review that proposes shorter periods has no Board resolution yet ("TBD").
- [S44] Cloudflare, "Cloudflare Registrar - Search and Buy Domains at Cost". https://www.cloudflare.com/domains/ Confirms: prices at what registries and ICANN charge, no markup; prices shown upfront; the box Search for a domain name; a sample .com name listed at \$10.46 with Renews at \$10.46/year; hairbygerta.com listed as Unavailable with no price; the Buy now button. The page shows no .com price until you search. The older address https://www.cloudflare.com/products/registrar/ leads to this page; the price is part of the Buy now button of a result, and while the pointer is on the result the button shows Buy now in place of the price (seen on the page on 13 October 2026).
- [S45] Wix Help Center, "Wix Domains: Canceling Your Domain". https://support.wix.com/en/article/canceling-a-wix-domain Confirms: the steps to cancel auto renew; you keep the domain until the end of the period; no refunds for domains.
- [S46] Cloudflare Docs, "FAQ" (last updated Aug 3, 2026). https://developers.cloudflare.com/registrar/faq/ Confirms: a transfer within 45 days of a renewal may add no extra year, a registry rule that applies to all registrars; billing when the code is entered; no refunds; five days to release; status on the Transfer domains page; Cloudflare nameservers are required.
- [S47] Cloudflare Docs, "Troubleshoot failed domain transfers". https://developers.cloudflare.com/registrar/troubleshooting/ Confirms: a verification email may go to the registrant contact email after a transfer; without verification within 15 days the domain is put on hold and its nameservers are replaced by a parking server until it is verified; the email is sent when the registrant email differs from the verified email of the Cloudflare account; after a renewal the 45 days count from the original expiration date.
- [S48] Cloudflare Docs, "Create account" (last updated Sep 17, 2026). https://developers.cloudflare.com/fundamentals/account/create-account/ Confirms: the sign-up address, fields and button.
- [S49] Cloudflare Docs, "Verify email address" (last updated Apr 20, 2026). https://developers.cloudflare.com/fundamentals/user-profiles/verify-email-address/ Confirms: verifying by the link in the email.
- [S50] Cloudflare Docs, "Zone status" (last updated Apr 21, 2026). https://developers.cloudflare.com/dns/zone-setups/reference/domain-status/ Confirms: a pending Free-plan domain is deleted after 28 days.
- [S51] Cloudflare Docs, "Set up a primary zone (Full setup)" (last updated Jul 29, 2026). https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/ Confirms: Domains, Onboard a domain, the Free plan, the record scan, where the nameservers are shown, DNSSEC off first, copy exactly, up to 24 hours, Active; its example table of records lists the records of the bare domain under the domain name itself.
- [S52] Cloudflare Docs, "Manage DNS records" (last updated May 6, 2026). https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-dns-records/ Confirms: the DNS Records page and its direct link; Add record, Type, Proxy status, TTL, Save; Edit; Delete and Delete again.
- [S53] Wix Help Center, "Activating DNSSEC for a Wix Domain". https://support.wix.com/en/article/activating-dnssec-for-a-wix-domain Confirms: the steps to turn off Privacy and DNSSEC protection; DNSSEC is only sold together with private registration; with the protection off, name and contact information can be seen in the WHOIS database; Turn On Protection switches it back on.
- [S54] Wix Help Center, "Viewing and Updating Your Wix Domain Contact Information". https://support.wix.com/en/article/viewing-and-updating-your-wix-domain-contact-information Confirms: changing the contact information locks the domain for 60 days; a new email address has to be confirmed from both the old and the new address; Wix recommends a registrant contact email that is not tied to the domain.
- [S55] ICANN, "2013 Registrar Accreditation Agreement", Whois Accuracy Program Specification. https://www.icann.org/en/contracted-parties/accredited-registrars/registrar-accreditation-agreement/2013-registrar-accreditation-agreement-17-09-2013-en Confirms: within 15 days of a transfer the registrar verifies the email address or the telephone number of the domain owner; without an answer it verifies by hand or suspends the registration.
- [S56] Cloudflare Docs, "Create billing profile" (last updated May 29, 2026). https://developers.cloudflare.com/billing/get-started/create-billing-profile/ Confirms: Billing, Subscriptions, Payment methods, Add Payment Method, Confirm; cards and PayPal are accepted; the older address without get-started leads to this page.
- [S57] Wix Help Center, "Connecting a Domain to Wix Using the Pointing Method". https://support.wix.com/en/article/connecting-a-domain-to-wix-using-the-pointing-method Confirms: the Wix site must be upgraded before a domain can be connected; the steps and button names, among them the note on Start Transfer and the outline with I logged in, I found my domain settings, I found the records and I updated my records; the A and CNAME values, which are also shown on the Wix domains page; replace the records; it may take up to 48 hours; no DNSSEC and no DNS proxy such as Cloudflare.
- [S58] Wix Help Center, "Connecting a Domain You Own to Your Wix Site". https://support.wix.com/en/article/connecting-a-domain-you-own-to-your-wix-site Confirms: connecting is not transferring; the domain stays with its outside registrar.
- [S59] Wix Help Center, "Turning the Auto Renewal Off for a Wix Premium Subscription". https://support.wix.com/en/article/turning-the-auto-renewal-off-for-a-wix-premium-subscription Confirms: Wix subscriptions renew automatically unless auto renew is turned off; auto renew can be turned back on before the end of the subscription period; for a business email it names other last clicks than the page on canceling a business email.
- [S60] Cloudflare Docs, "Proxy status" (last updated Apr 21, 2026). https://developers.cloudflare.com/dns/proxy-status/ Confirms: the two states Proxied (orange cloud) and DNS only (gray cloud); a proxied record is answered with Cloudflare addresses; proxying is on by default when a domain is added in the dashboard; Cloudflare's general recommendation to proxy web records.
- [S61] Cloudflare Docs, "DNS record types". https://developers.cloudflare.com/dns/manage-dns-records/reference/dns-record-types/ Confirms: what A, AAAA, CNAME, MX and TXT records do; the fields Name (with @ for the bare domain), IPv4 address and Target; the content of a TXT record.
- [S62] GitHub Docs, "Securing your GitHub Pages site with HTTPS". https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https Confirms: the Enforce HTTPS steps and that it redirects visitors to HTTPS; the automatic DNS check, the Let's Encrypt certificate and the check mark; Remove and Save again restarts the process; extra A, AAAA or CNAME records, or records not pointing to GitHub, can stop the certificate; the page does not mention Cloudflare or a proxy.
- [S63] GitHub Docs, "About repositories". https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories Confirms: a repository holds your files and each file's revision history.
- [S64] GitHub Docs, "Managing a custom domain for your GitHub Pages site". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site Confirms: the four A record addresses; the www CNAME points to the user name followed by .github.io without the repository name; Settings, Pages, "Custom domain", Save and Remove; add the domain in GitHub before changing DNS, and the warning about what can happen otherwise; the tip to verify the domain first; the CNAME file that GitHub adds and the need to pull it; the bare domain redirects to www; DNS changes can take up to 24 hours; Enforce HTTPS can take up to 24 hours to become available; people with admin permissions for the repository can set the custom domain; the dropdown menu (a three-dot icon) that holds Settings when the tab is not shown; the page does not mention Cloudflare or a proxy.
- [S65] GitHub Docs, "Troubleshooting custom domains and GitHub Pages". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages Confirms: up to an hour until HTTPS works; removing and adding the domain again after DNS changes; the CNAME file must stay in the repository; the CAA rule; clearing the browser cache; what to do when the domain is already taken; the page does not mention Cloudflare or a proxy.
- [S66] GitHub Docs, "Verifying your custom domain for GitHub Pages". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages Confirms: what verifying protects against, the steps and button names, the wait of up to 24 hours, and that the TXT record must be kept; once a domain is verified, only repositories owned by the account that verified it may publish a GitHub Pages site to the domain or its immediate subdomains; the page does not describe how to remove a verification; verifying frees a domain that another GitHub user has taken; the page does not mention Cloudflare or a proxy.
- [S67] Cloudflare Docs, "Import and export records". https://developers.cloudflare.com/dns/manage-dns-records/how-to/import-and-export/ Confirms: Import and Export, then Export, downloads the records.
- [S68] Cloudflare Docs, "Create zone apex record". https://developers.cloudflare.com/dns/manage-dns-records/how-to/create-zone-apex/ Confirms: a record for the bare domain is made with @ as its Name.
- [S69] Cloudflare Docs, "Use cases" (Proxy status). https://developers.cloudflare.com/dns/proxy-status/use-cases/ Confirms: for a site hosted on another platform, set the record to DNS-only unless the platform explicitly supports Cloudflare's proxy; proxying can cause SSL errors and redirect loops.
- [S70] GitHub Docs, "About custom domains and GitHub Pages". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages Confirms: GitHub Pages supports custom domains; the page does not mention Cloudflare or a proxy.
- [S71] Cloudflare Docs, "Time to Live (TTL)". https://developers.cloudflare.com/dns/manage-dns-records/reference/ttl/ Confirms: Auto means 300 seconds (five minutes); a local DNS cache may take longer to update.
- [S72] Cloudflare Docs, "Vendor-specific DNS records", section "Wix". https://developers.cloudflare.com/dns/manage-dns-records/reference/vendor-specific-records/ Confirms: with DNS at Cloudflare, a domain is connected to Wix by pointing, and all its records should be DNS-only.
- [S73] Cloudflare Docs, "Set up email records" (last updated Apr 16, 2026). https://developers.cloudflare.com/dns/manage-dns-records/how-to/email-records/ Confirms: Email Routing is free email forwarding for domains that only need to receive mail; sending and receiving from the domain needs an SMTP provider.
- [S74] Cloudflare Docs, "Pricing" (Email Service, last updated Jun 9, 2026). https://developers.cloudflare.com/email-service/platform/pricing/ Confirms: Email Routing is available on the Workers Free plan; inbound emails are listed as Unlimited; the paid plan Workers Paid.
- [S75] Cloudflare Docs, "Email routing rules and addresses". https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/ Confirms: what a destination address and a routing rule are; sign in and select your account; a rule stays disabled until its destination is verified; pending addresses and resending the verification email; deleting a destination address disables its rules; the Active and Disabled status; Edit; the Catch-all rule on the Routing Rules tab forwards every email sent to the domain to one destination.
- [S76] Cloudflare Docs, "Domain configuration". https://developers.cloudflare.com/email-service/configuration/domains/ Confirms: Cloudflare adds the records itself; MX, SPF and DKIM records on the root domain with their names and values; Settings, the DNS records section, Locked and Unlocked; locked records cannot be edited under DNS > Records; Unlock; existing MX records must be removed or updated and Email Routing cannot be used with external mail servers; existing SPF records are merged into one, with the merged example; Disable Email Routing and what it removes; add the new provider's records before disabling.
- [S77] Public DNS records of hairbygerta.com (MX, TXT and NS). Confirms: a public record, not a help page. Read on 12 October 2026 with a lookup through Cloudflare's public resolver 1.1.1.1: five Google mail servers, one Google SPF record, name servers at Wix.
- [S78] Cloudflare Docs, "Troubleshooting". https://developers.cloudflare.com/email-service/reference/troubleshooting/ Confirms: more than one SPF record is not allowed; delete the incorrect SPF record; an existing SPF record on the root domain is changed to include Cloudflare's; only when unsure which one to keep, delete all SPF records under DNS > Records and onboard again to let Cloudflare add its own.
- [S79] Cloudflare Docs, "Email logs". https://developers.cloudflare.com/email-service/observability/logs/ Confirms: the Activity log and the labels Forwarded, Dropped, Rejected, Delivery failed and Error.
- [S80] Cloudflare Docs, "Postmaster". https://developers.cloudflare.com/email-service/reference/postmaster/ Confirms: Email Routing does not support sending or replying from your domain, replies go out from the destination address; non-delivery reports are not forwarded to the sender; incoming mail must pass SPF or DKIM; senders on block lists are rejected.
- [S81] Cloudflare Docs, "Limits". https://developers.cloudflare.com/email-service/platform/limits/ Confirms: inbound messages over 25 MiB are rejected; one routing rule maps one email pattern to one destination.
- [S82] GitHub Docs, "Committing and reviewing changes to your project in GitHub Desktop". https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop Confirms: what a commit is; the Changes tab lists changed files; the Summary field; the Commit to BRANCH button under the Description field (for this site the branch is main); Push origin; Discard Changes, shown in a context menu in the page's picture, and the "Confirm Discard Changes" window; pre-commit hooks run automatically when you commit, if the repository has them; the Bypass Commit Hooks option.
- [S83] GitHub Docs, "Pushing changes to GitHub from GitHub Desktop". https://docs.github.com/en/desktop/making-changes-in-a-branch/pushing-changes-to-github-from-github-desktop Confirms: pushing sends the committed changes to the repository on GitHub.
- [S84] GitHub Docs, "Reverting a commit in GitHub Desktop". https://docs.github.com/en/desktop/managing-commits/reverting-a-commit-in-github-desktop Confirms: History, Revert Changes in Commit; the original commit remains in the repository's history; several commits are best reverted from newest to oldest, otherwise merge conflicts are possible.
- [S85] GitHub Docs, "Installing GitHub Desktop". https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop Confirms: the download page, the Download for Windows button, the setup file, and that GitHub Desktop launches after installation.
- [S86] GitHub, program text of GitHub Desktop (not a help page). https://github.com/desktop/desktop/tree/development/app/src/ui Confirms: read on 13 October 2026 in the files welcome/start.tsx and app.tsx (the first start shows "Welcome to GitHub Desktop" with Sign in to GitHub.com and no menu bar), changes/commit-message.tsx (the commit button names the number of files, in the form Commit 6 files to main) and changes/filter-changes-list.tsx (on Windows the right-click menu of a changed file says Discard changes).
- [S87] GitHub Docs, "Authenticating to GitHub in GitHub Desktop". https://docs.github.com/en/desktop/installing-and-authenticating-to-github-desktop/authenticating-to-github-in-github-desktop Confirms: File, Options, the Accounts pane, the "Sign Into" button, Continue With Browser, signing in in the browser and returning to GitHub Desktop; the two-factor code, if the account has one.
- [S88] GitHub Docs, "Configuring Git for GitHub Desktop". https://docs.github.com/en/desktop/configuring-and-customizing-github-desktop/configuring-git-for-github-desktop Confirms: File, Options, Git, the "Name" field, the "Email" dropdown menu, Save; anyone can see the email address in the Git configuration when commits are public.
- [S89] GitHub Docs, "Adding a repository from your local computer to GitHub Desktop". https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop Confirms: File, Add local repository, Choose..., Add repository.
- [S90] GitHub Docs, "Cloning and forking repositories from GitHub Desktop". https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop Confirms: File, Clone Repository creates a local copy of a repository on the computer.
- [S91] GitHub Docs, "Syncing your branch in GitHub Desktop". https://docs.github.com/en/desktop/working-with-your-remote-repository-on-github-or-github-enterprise/syncing-your-branch-in-github-desktop Confirms: Fetch origin checks for new commits on GitHub, Pull origin brings them into the local copy.
- [S92] Google Chrome Help, "Chrome keyboard shortcuts". https://support.google.com/chrome/answer/157179 Confirms: reload the current page ignoring cached content with Shift + F5 or Ctrl + Shift + r on Windows and with Command + Shift + r on a Mac.
- [S93] Microsoft Support, "Keyboard shortcuts in Microsoft Edge". https://support.microsoft.com/en-us/microsoft-edge/keyboard-shortcuts-in-microsoft-edge-50d3edab-30d9-c7e4-21ce-37fe2713cfad Confirms: Ctrl+Shift+R reloads the current page, ignoring cached content.
- [S94] GitHub Docs, "Configuring a publishing source for your GitHub Pages site". https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site Confirms: when a site is published from a branch, changes pushed to that source branch are published to the site; the steps Settings, Pages, "Build and deployment", "Source", Deploy from a branch, the branch dropdown menu, the folder dropdown menu with the root folder as its default, Save; the site is deployed by a GitHub Actions workflow run that you do not have to write, and errors show in the workflow runs of the repository.
- [S95] GitHub Docs, "Working with Git hooks in GitHub Desktop". https://docs.github.com/en/desktop/making-changes-in-a-branch/working-with-git-hooks-in-github-desktop Confirms: when a commit hook fails, GitHub Desktop shows its output and offers Commit anyway; Bypass Commit Hooks and Commit anyway commit without the check.
- [S96] GitHub Docs, "GitHub glossary". https://docs.github.com/en/get-started/learning-about-github/github-glossary Confirms: a branch is a parallel version of a repository.
- [S97] GitHub Docs, "Editing files". https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files Confirms: browse to the file; the pencil icon labeled "Edit file" in the upper right corner of the file view; Commit changes...; the "Commit message" field; the choice between the current branch and a new branch, and GitHub's advice to use a new branch; the Commit changes button.
- [S98] GitHub Docs, "Getting changes from a remote repository". https://docs.github.com/en/get-started/using-git/getting-changes-from-a-remote-repository Confirms: a pull fetches the changes from GitHub and merges them into the copy on the computer.
- [S99] Apple Support, "Keyboard shortcuts and gestures in Safari on Mac". https://support.apple.com/guide/safari/keyboard-shortcuts-and-gestures-cpsh003/mac Confirms: in Safari, Shift-Command-R opens Reader.
- [S100] Apple Support, "If Safari doesn't work as expected on Mac". https://support.apple.com/102564 Confirms: reload a page in Safari from the View menu with Reload Page, or with Command-R.
- [S101] Wix Help Center, "Domain Life Cycle". https://support.wix.com/en/article/domain-life-cycle Confirms: the Grace Period (about 30 days, no extra fee, domain no longer connected to the site, Extend Registration, private auction possible in the last 10 days); the Redemption Period (about 30 days, fee varies and is shown on the Domains page, Keep Domain, not guaranteed, up to 7 days); Pending Delete, then open to anyone after 5 to 10 days.
- [S102] ICANN, "5 Things every Domain Name Registrant should know about ICANN's Expired Registration Recovery Policy (ERRP)". https://www.icann.org/resources/pages/registrant-about-errp-2018-12-07-en Confirms: the website and email of an expired name are interrupted before it is deleted and during redemption; a Redemption Grace Period of 30 days in which the name can be restored; the registrar may charge a fee.
- [S103] Wix Help Center, "Wix Domain Renewal Payment Failure". https://support.wix.com/en/article/wix-domain-renewal-payment-failure Confirms: the 30 day grace period at no extra fee; a redemption fee of \$100; if the payment attempt fails, the domain expires on the anniversary of the original payment.
- [S104] Wix Help Center, "Transferring an Expired Wix Domain to Another Domain Host". https://support.wix.com/en/article/transferring-an-expired-wix-domain-to-another-domain-host Confirms: an expired domain can be transferred only during the grace period, not in the redemption period; a \$100 retrieval fee; when extending a domain, changing its contact info locks it from transfer for 60 days.
- [S105] Wix Help Center, "Extending Your Wix Domain Subscription". https://support.wix.com/en/article/extending-your-wix-domain-subscription Confirms: the steps Domains, Extend, registration period, Continue, privacy option, Continue, payment information, Submit Purchase.
- [S106] Google Workspace Help, "Cancel Google Workspace" (last updated 9 October 2026). https://knowledge.workspace.google.com/admin/billing/cancel-google-workspace Confirms: after a subscription bought from Google is canceled, user data is deleted and cannot be restored; customers of a reseller are sent to a different page.
- [S107] Wix Help Center, "Closing Your Wix Account". https://support.wix.com/en/article/closing-your-wix-account Confirms: closing the account cannot be undone and you lose access to everything in it; you do not need to wait for a canceled subscription to expire; a canceled domain stays registered until it expires; the account can stay open for free after the premium subscriptions are canceled.
- [S108] GitHub Docs, "GitHub Pages limits". https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits Confirms: GitHub Pages is available in public repositories with GitHub Free; the 1 GB site limit and the 100 GB soft bandwidth limit; the rule against using Pages as free hosting for an online business or shop.
- [S109] Cloudflare, "Pricing". https://www.cloudflare.com/plans/ Confirms: the Free plan at \$0 a month with DNS among its core features; the paid plans Pro and Business; Cloudflare Registrar "Starting at \$7.85" with no domain ending named; a paid tier under Workers.
- [S110] Cloudflare Docs, "Sales tax". https://developers.cloudflare.com/billing/understand/sales-tax/ Confirms: Cloudflare collects sales tax based on the billing address; in the US by the postal code of the address on file. The page does not list the states.
- [S111] Cloudflare Docs, "Renew domains" (last updated Apr 24, 2026). https://developers.cloudflare.com/registrar/account-options/renew-domains/ Confirms: auto renew on by default; renewal at the list price set by the registry; first try about 30 days before expiry; a renewal can fail, then an email and three more tries, then manual renewal (Manage domains, Manage, Renew/Extend Domain, Renew, Purchase); the monthly emails to the Super Admin (domains renewing within 45 days, domains expiring in 60 to 90 days) and the warnings to the registrant contact; the 30 day Redemption Grace Period, a possible restoration fee and no transfer during it; renewals are final, no refunds.
- [S112] Square Support Center, "Learn about Square fees". https://squareup.com/help/us/en/article/6109-fees-and-payments-faqs Confirms: processing fees are taken out of the total amount of each transaction; the same rates per plan.
- [S113] Wix Help Center, "Downloading Invoices for Wix Subscriptions and Services". https://support.wix.com/en/article/downloading-invoices-for-wix-subscriptions Confirms: the address of the Billing History page; the More Actions icon; View Invoice.
- [S114] Wix Help Center, "Managing Invoices Paid for Wix Services". https://support.wix.com/en/article/managing-invoices-paid-for-wix-services Confirms: the Billing History page holds all invoices for services paid at Wix; the All Dates drop-down; services with the same renewal date may share one invoice.
- [S115] GitHub Docs, "Creating a new repository". https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository Confirms: the plus icon labeled "Create something new", New repository, the Owner dropdown menu, the "Repository name" field, choosing a visibility, the optional README, .gitignore and license, Create repository.
- [S116] GitHub Docs, "Adding locally hosted code to GitHub". https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github Confirms: do not initialize the new repository with README, license or gitignore files, to avoid errors; copy the repository address from the Quick Setup page; Git Bash on Windows; the commands git init -b main, git add ., git commit -m "First commit", git remote add origin REMOTE-URL and git push -u origin main.
