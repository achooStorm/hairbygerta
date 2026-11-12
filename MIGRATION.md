# Moving hairbygerta.com off Wix: a step by step guide

This guide is for Gerta, the owner of Hair & Makeup by Gerta, and for her helper. It shows how the salon website moves from Wix to the new site in the folder `hairbygerta`, which the helper publishes on GitHub Pages. The address hairbygerta.com, called the domain, moves once, from Wix straight to Porkbun, a company that registers domains [S141]. Mail sent to info@hairbygerta.com is then forwarded for free to Gerta's Gmail address [S132]. The guide shows what can be done now, what was checked in the Wix account, how the move goes day by day, and what it costs afterwards.

Four things to know before you start.

- **One move, with fixed dates.** On 2 November 2026 the Wix account showed that the Wix site plan and the business email end on the evening of Thursday 26 November 2026, New York time. The domain's registration at Wix expires the same evening [S27]. Auto renew is off for all three. With auto renew off, a Wix subscription does not renew [S59], so nothing has to be canceled. Before that evening the domain moves to Porkbun. Your helper starts the transfer on Monday 9 November 2026, or at the latest on Monday 16 November 2026. [Section 2](#2-what-was-checked-in-wix-on-2-november-2026) has the end dates, and [Section 3](#3-moving-the-domain-from-wix-to-porkbun-step-by-step) has the steps of the move.
- **The Wix site keeps running until the transfer completes.** Nothing in Sections 1 and 2 changes it. When the transfer completes, Wix disconnects the Wix site from the domain [S35]. The same day your helper points the address at the new site ([Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages)) and turns on the email forwarding ([Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail)).
- **You can look at the new site in the meantime.** On the computer today, and on the internet at the preview address https://achoostorm.github.io/hairbygerta/ once the new site is published. [Section 1, Part 1](#part-1-look-at-the-new-site) shows both.
- **The photos are the one difference.** 26 photos of the Wix site cannot move to the new site. [Section 8, Part 4](#part-4-the-14-shutterstock-photos) says why. The new site does not show them. Each one has a spot that is left out of its page until you put in a photo of your own, and the pages look finished without it. Never save, copy or upload a photo from the Wix site.

How to read this guide.

- **Your helper** is the person who built the new site and helps you with the computer steps.
- **The helper's accounts.** The Wix account that owns the salon site is in the helper's name, and so is the domain hairbygerta.com. The helper is its registrant, the person listed as the domain's owner. The helper also opens the Porkbun account, with the helper's personal email address. The GitHub account achooStorm, which holds the new site, is the helper's too. A step that starts with **Your helper signs in** happens inside one of these accounts. The helper signs in with their own password and sign-in codes, and nobody else types them. Gerta cannot do those steps alone. She also needs the helper for every later change at Porkbun and on GitHub, for example to publish a photo ([Section 6](#6-how-to-replace-a-placeholder-with-a-real-photo)) or to change the phone number on the site ([Section 7](#7-booking-by-phone)).
- **Gerta's own accounts.** The business mailbox info@hairbygerta.com is Gerta's. Wix sells it through Google Workspace, Google's paid email service [S20], and Gerta is its administrator. Her Gmail, where the forwarded mail will arrive, is her own too. A step that starts with **Gerta signs in** happens inside one of these. Gerta does it herself, or her helper does it with Gerta next to them, saying yes to each step. Nobody signs in as Gerta, asks for her passwords or codes, or types in her bank or card details for her.
- **Gerta's decisions.** The site and the mail are for Gerta's salon, so some choices are hers alone, even when the helper does the clicks. She chooses the photos. She decides whether the free email forwarding is enough for her mail, and whether the domain is locked to the helper's GitHub account. Step 9 of [At a glance](#at-a-glance) says by when. [Section 4](#whose-github-account-this-is-and-what-gerta-decides) explains what the helper's GitHub account means for the address hairbygerta.com.
- **Bold words** in the steps are the names of buttons, menus, fields and pages, written the way the official help pages write them.
- A marker like [S35] points to the list [Official help pages used](#official-help-pages-used) at the end. Every statement about how Wix, Porkbun, GitHub or Google works comes from one of those pages. The pages were opened on 12 or 13 October 2026 or on 2 November 2026, and the start of that list says which.
- Rules, prices and screens change. Porkbun's price for a .com domain, for example, went up on 1 November 2026 [S140]. If a screen does not match a step, stop. Open the help page behind the marker, or ask your helper.
- Dates are written with the month as a word, for example 26 November 2026, so the day and the month cannot be mixed up.

## At a glance

Tick each step when it is done. The order matters. The link in each step leads to the part of this guide that explains it. Step 1 is already done.

**Already done**

1. [x] On Monday 2 November 2026 the end dates were checked in the Wix account and in the public record [S27]. The Wix site plan, the domain's registration at Wix and the business email all end on the evening of Thursday 26 November 2026, New York time, and none of them renews [S59]. See [Section 2, The end dates](#the-end-dates).

**Now, while everything stays on Wix**

2. [ ] Look at the new site on the computer. See [Section 1, Part 1](#part-1-look-at-the-new-site).
3. [ ] Collect your own photos. See [Section 1, Part 2](#part-2-collect-your-own-photos).
4. [ ] Booking stays by phone and needs no setup. Every **Call 347-671-5095** button on the new site calls the number, and **Text Gerta** starts a text message to it. See [Section 1, Part 3](#part-3-booking-stays-by-phone).
5. [ ] Your helper publishes the new site, so that it opens at the preview address. Then you look at every page there together. Do this before the transfer starts in step 10, because the new site has to be ready when the Wix site leaves the address [S35]. Only the helper can publish, because the GitHub account is theirs. See [Section 1, Part 4](#part-4-your-helper-publishes-the-new-site-the-first-time).
6. [ ] Read [Section 8, What cannot be undone](#8-what-cannot-be-undone) once, before anything is changed at Wix.

**The move, in November 2026**

7. [ ] By Thursday 5 November 2026, your helper turns off **Privacy and DNSSEC protection** at Wix. DNSSEC is a security seal on the domain's settings, and Porkbun recommends deleting DNSSEC records before a transfer [S125]. Wix sells DNSSEC only together with private registration, so the same switch makes the name and contact details of the domain's owner visible in the public record, called WHOIS [S53]. They stay visible until Porkbun's free WHOIS privacy covers them after the move [S121] [S137]. The person listed as the domain's owner decides whether to accept that. Today that is the helper. The switch is on the **Edit contact info** page [S53]. Change nothing else there, because a change to the contact details locks the domain for 60 days [S38] [S54]. Then your helper checks in the public record that DNSSEC is off, before going on [S27] [S28]. See [Section 3, Part A](#part-a-turn-off-privacy-and-dnssec-at-wix).
8. [ ] Before Monday 9 November 2026, your helper gets Porkbun ready. The Porkbun account is the helper's, opened with the helper's personal email address. See [Section 3, Part B](#part-b-get-porkbun-ready).
9. [ ] Before Monday 9 November 2026, Gerta makes two decisions and tells her helper. First, whether the free email forwarding is enough for her mail. It only receives mail and passes it on, and her replies go out from her Gmail address [S132] [S135]. Section 5 explains this under [Before you turn on forwarding](#before-you-turn-on-forwarding) and [Limits of the forwarding](#limits-of-the-forwarding). Second, whether the domain is locked to the helper's GitHub account. See [Whose GitHub account this is, and what Gerta decides](#whose-github-account-this-is-and-what-gerta-decides) in Section 4.
10. [ ] On Monday 9 November 2026, or at the latest on Monday 16 November 2026, your helper starts the transfer. See [Section 3, Part C](#part-c-start-the-transfer), and [The dates](#the-dates) for why these dates. Wix sends the transfer code (the authorization code) to the registrant contact email [S35], which is the helper's personal email address. The helper enters the code at Porkbun, and the transfer is paid there [S120]. Since 1 November 2026 a .com transfer at Porkbun costs \$11.81 [S140] [S141]. Read the price on the screen before paying. The transfer adds one year to the domain [S121] [S124]. If the transfer cannot start by Monday 16 November 2026, your helper extends the domain at Wix before it expires [S105] and moves it later. See [If something goes wrong](#if-something-goes-wrong).
11. [ ] While the transfer runs, your helper keeps an eye on it. It usually takes five to seven days, and Porkbun sends an email when it is done [S123]. See [Section 3, Part D](#part-d-while-the-transfer-runs).
12. [ ] The day the transfer completes, your helper points hairbygerta.com at the new site. Wix disconnects the Wix site when the transfer completes [S35], so do this the same day. Until it is done, the address may show no website. See [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages).
13. [ ] The same day, your helper turns on the free email forwarding from info@hairbygerta.com to Gerta's Gmail address [S132], unless Gerta chose another way in step 9. Then Gerta tests it. See [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail).
14. [ ] Once the forwarding works, and by Friday 20 November 2026 at the latest, Gerta backs up the mailbox info@hairbygerta.com with Google Takeout [S32]. See [Section 2, Back up the mailbox](#back-up-the-mailbox).
15. [ ] Thursday 26 November 2026 is Thanksgiving, and nothing has to be done that day. In the evening, New York time, the Wix site plan and the business email end by themselves. There is nothing to cancel and nothing more to pay Wix. By then the domain is at Porkbun. A domain still at Wix that was not extended would expire that evening [S27]. See [Section 8](#8-what-cannot-be-undone).

**Any time, and afterwards**

16. [ ] Put your own photos in place of the placeholders, one at a time. This works before and after the move. See [Section 6](#6-how-to-replace-a-placeholder-with-a-real-photo).
17. [ ] Once a year, check with your helper what the domain costs at Porkbun. It is the one bill left after the move, and Porkbun says the .com price is expected to rise about 7% a year [S140]. See [Section 9](#9-yearly-cost-after-the-move).

## 1. What can be done now without touching Wix

Nothing in this section changes the Wix site, the domain or your email. Do Part 1 before Part 2. Part 3 only explains how booking works and has no steps. Part 4 is for your helper and can be done on any day.

### Part 1: Look at the new site

**On the internet, once the site is published.** Your helper publishes the site. [Part 4](#part-4-your-helper-publishes-the-new-site-the-first-time) shows how. After it, the new site is at this preview address (a temporary web address, used until hairbygerta.com points to the new site):

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

The site shows two photos today, both your own. 26 more spots wait for your own photos. A spot without a photo is left out of its page, so you will not see an empty box.

### Part 2: Collect your own photos

26 of the photos on the old site cannot move with you. Shutterstock photos bought through Wix may only be used on Wix and cannot be downloaded [S4]. The free Wix photos, and the photos that came with the Wix template, are for use within Wix only [S5].

A photo is safe to use only if one of these is true:

- You took it yourself.
- Someone else took it and you have their written permission to use it on your website. Keep the email or message.
- It is a stock photo you bought yourself outside Wix, and you still have the license that allows website use. Wix itself says to check which license you bought [S6].

Not safe: a photo saved or screenshotted from the old Wix site, anything in the folder `hairbygerta-wix-only-photos`, and photos found on Google, Pinterest or Instagram. If a client can be recognised in a photo, get the client's written OK too.

1. Start the preview on the computer (Part 1).
2. Open the table [Which name is used where](#which-name-is-used-where) in Section 6. It lists the 26 spot names, for example `home-smile`, and the pages that show each one.
3. Pick your own photo for that spot. Every spot is tall, like a phone photo held upright. The page crops the photo to fit, so keep the hair or face near the middle.
4. Copy the photo you picked into a new folder of its own, for example a folder called salon-photos in your Pictures. Use the original photo file, not a screenshot. Do not put it into the `hairbygerta` folder yet.
5. Write down the placeholder's file name for this photo, and a few words on what the photo shows.
6. Repeat steps 2 to 5 for the next spot.

When a photo is ready to go onto the site, follow [Section 6](#6-how-to-replace-a-placeholder-with-a-real-photo). It shows how to save the photo in the right size and under the right name, and how to publish it. Section 6 also has a table of all 26 placeholder names. If those computer steps are not for you, give your helper the folder with your photos and your notes.

There are 26 placeholder names. You do not need all of them at once. A spot you do not fill is left out of its page. Some photos are used on more than one page.

**The logo.** The logo file is only 225 px wide and 225 px tall (px means pixels, the dots a picture is made of), so it can look a little soft on sharp screens. Ask whoever designed the logo for the original artwork (a vector file such as SVG, AI, EPS or PDF, or a large PNG). A sharper logo can then be put in later. Nothing has to change now.

### Part 3: Booking stays by phone

The owner of Le Vigne Hair Salon wants clients to use the salon's own booking, and there is no online booking link for it. So the new site takes no bookings online. Its Services page lists the services, and the **Call 347-671-5095** button there calls the number. There is nothing to set up. [Section 7](#7-booking-by-phone) says where the phone number is written, in case it ever changes.

### Part 4: Your helper publishes the new site the first time

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

## 2. What was checked in Wix on 2 November 2026

On Monday 2 November 2026 the Wix account and the public record of the domain were checked. Nothing was changed. The main result is three end dates, all on the same evening. This section gives them and shows how to see them again. It also shows how Gerta backs up the business mailbox before it ends.

The check also found three things that later sections use.

- DNSSEC (a security seal on the domain's settings) is switched on for hairbygerta.com [S27]. [Section 3, Part A](#part-a-turn-off-privacy-and-dnssec-at-wix) turns it off before the transfer.
- The registrant contact email of the domain (the email address of the domain's owner at Wix) is the helper's personal email address. Wix sends the transfer code to that address [S35]. See [Section 3, Part C](#part-c-start-the-transfer).
- The DNS records at Wix are the records of the Wix site, two Google verification records and the records of the Google mailbox. Sections 4 and 5 say what happens to them.

### The end dates

| What | Ends | Auto renew |
|---|---|---|
| Wix site plan (Core) | Thursday 26 November 2026, in the evening, New York time | Off |
| Domain hairbygerta.com, registered at Wix | Thursday 26 November 2026 at 8:04 PM, New York time | Off |
| Business email info@hairbygerta.com | Thursday 26 November 2026, in the evening, New York time | Off |

Words used in this table.

- The **site plan** is the paid Wix plan that keeps the Wix site on hairbygerta.com. Wix also calls it a Premium plan [S19]. This one is called Core.
- The **domain** is the address of the website, hairbygerta.com. Today it is registered at Wix [S27].
- The **business email** is the mailbox info@hairbygerta.com. Wix sells it through Google Workspace, Google's paid email service [S20]. This one is the Business Starter plan with one mailbox, and Gerta is its administrator.
- **Auto renew** means that Wix charges a card by itself to keep a service running. With auto renew off, a Wix subscription does not renew [S59].

Why all three say the same evening. The public record gives the end of the domain as 27 November 2026 at 01:04 UTC [S27]. UTC is the world's standard clock time. In New York that moment is 8:04 PM on Thursday 26 November 2026. The site plan and the business email end with their billing period on 27 November 2026 in UTC too, which is also the evening of 26 November 2026 in New York. So a page may show 26 November or 27 November. Both mean the same evening. That day is Thanksgiving, so plan no step for that day.

What this means for you.

- Nothing has to be canceled, and nothing more is paid to Wix. Each of the three ends by itself at the end of its paid period [S19] [S30] [S45] [S59].
- The domain must move to Porkbun before that evening. That is [Section 3](#3-moving-the-domain-from-wix-to-porkbun-step-by-step).
- What happens on that evening to the Wix site, the domain and the mailbox is in [Section 8](#8-what-cannot-be-undone).
- Do not switch auto renew back on, unless Gerta and your helper have decided to keep something at Wix. **Turn Auto Renew On** switches a site plan back on [S24], and **Turn auto renew on** does the same for a business email [S30]. Wix does not refund renewals [S19] [S30].

To see the dates again, follow the steps below. You only look and change nothing. Use a computer, not a phone. Click only the buttons named in the steps. If a page asks you to pay, renew, cancel or confirm, close it. To hover means to rest the mouse pointer on something without clicking.

**The site plan and the business email**

1. **Your helper signs in** to wix.com with the Wix account that owns the salon site. That account is in the helper's name.
2. Open the Wix help page "Viewing Your Site Plans and Other Subscriptions" at https://support.wix.com/en/article/viewing-your-premium-plans [S21].
3. Click **View Subscriptions**. The **Premium Subscriptions** page opens. It lists the site plan and everything else bought from Wix [S21]. Wix shows the expiration date of a plan on this page [S19].
4. In the row of the site plan, read the **Upcoming payment** column and hover over the **Info** icon next to it [S22].
5. Do the same in the row of the business email [S29].
6. Open manage.wix.com/account/mailboxes. This is the Business Email page that Wix's help links to. Check that info@hairbygerta.com is listed there [S20].

The **Upcoming payment** column shows the date of the next renewal payment. With auto renew off, that date can differ a little from the end date [S22] [S29]. If a row does not match the table above, copy it word for word and show your helper.

**The domain**

7. Click the user panel at the top right (the small menu for your own account) [S25].
8. Click **Account Settings**, then **Domains** in the menu on the left [S25].
9. Find hairbygerta.com under **Assigned Domains** [S25]. The page shows its expiry date and its payment renewal date [S25]. On 2 November 2026 it said "Expires on Nov 26, 2026", with auto renew off.

If hairbygerta.com is not on the **Domains** page, you are most likely signed in to a different Wix account. The help page from step 2 links to an account email locator [S21].

**The public record**

The registry is the organization that keeps the official list of all .com addresses. Anyone can look up a domain's record in that list at https://lookup.icann.org [S28]. On 2 November 2026 the record of hairbygerta.com showed the registrar Wix.com Ltd., registered on 27 November 2025 and expiring on 27 November 2026 at 01:04 UTC [S27]. After the move in Section 3, the record names Porkbun and the new expiry date.

### Back up the mailbox

Gerta makes a copy of the whole mailbox info@hairbygerta.com with **Google Takeout**, Google's tool for downloading a copy of your data [S32]. After the business email ends, nobody can read, receive or send mail in it any more [S31]. This copy keeps the old mail. The Wix help pages about the business email give no steps for exporting mail [S30] [S31] [S33].

**When to do it.** After the forwarding in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) works, and by Friday 20 November 2026 at the latest.

- Why after the forwarding works. From then on the domain's mail goes to Porkbun, which passes it on to Gerta's Gmail address [S132]. So new mail stops landing in this mailbox, and a backup made then holds all its mail. The file may not hold mail that arrives after you ask for it [S32].
- Why by 20 November 2026. The export can take from a few minutes to a few days [S32], and the mailbox ends on the evening of 26 November 2026.
- If the forwarding does not work yet on Friday 20 November 2026, do not wait for it. Make the backup that day. Then make one more as soon as the forwarding works, if that is still before 26 November 2026.

**The steps**

1. **Gerta signs in** at gmail.com with info@hairbygerta.com and its password [S33].
2. Go to takeout.google.com [S32].
3. Check that the picture or initial at the top right belongs to info@hairbygerta.com, not to a personal Gmail account. If it shows another account, click the picture or initial and select info@hairbygerta.com before you go on [S33].
4. Uncheck the box beside every product you do not need. Keep the box for your email (Gmail) checked. Keep Contacts, Calendar and Drive checked too if you use them [S32].
5. Select **Next step** [S32].
6. Under delivery method choose **Send download link via email** [S32].
7. Choose **One-time archive**. Archive is Google's word for the backup file [S32].
8. Choose **Zip files**. A zip file is one file that holds many files [S32]. Leave **Archive size** as it is. If your data is larger than that size, Google makes more than one file [S32].
9. Select **Create export** [S32].
10. Wait for the email from Google. It can take from a few minutes to a few days. Most people get it the same day [S32]. Look for it in the inbox of info@hairbygerta.com. If it is not there, look in Gerta's Gmail as well, spam folder included.
11. In that email select **Download archive** and follow the steps on the screen [S32]. If there is more than one file, download every one of them.
12. Save the file, or all the files, in a new folder called email-backup in your Documents. Never save them in the `hairbygerta` folder, because the files in that folder are published as the public website.
13. Copy the file or files to a USB stick as well.
14. Write down the date of the backup.

Do steps 11 to 13 within a week. The archive expires in about 7 days and can be downloaded 5 times [S32].

If Takeout says you cannot download, stop. Takeout is allowed by default for Google Workspace, but an administrator can block it [S34]. Gerta is the administrator of this mailbox. **Gerta signs in** to the Google Admin console, together with your helper, and looks under **Menu**, **Data**, **Data import & export**, **Google Takeout** [S34].

## 3. Moving the domain from Wix to Porkbun, step by step

This section moves the domain hairbygerta.com from Wix to Porkbun, in one move. After the move Porkbun registers and renews the domain and holds its DNS records [S35] [S121]. Your helper does every step in this section. It starts with Part A, by Thursday 5 November 2026.

### Read this first

**Who signs in.** The Wix account and the domain are in your helper's name. Your helper is the registrant, the person listed as the domain's owner. So every Wix step here starts with **Your helper signs in**. Wix lets only the site owner move a domain away, or a co-owner who owns the payment method used for the domain [S35]. Your helper also opens the Porkbun account, with the helper's personal email address ([Part B](#part-b-get-porkbun-ready)). Nobody else types the helper's passwords or asks for the transfer code. Gerta does not sign in anywhere in this section. She should still know the dates, because the website and the email change on the day the move is done.

Words used in this section.

- **Registrar** means the company where a domain is registered and renewed. For hairbygerta.com that is Wix today [S27], and Porkbun after the move.
- **Transfer** means the move of a domain from one registrar to another.
- **Authorization code** (also called EPP code) is a one-time password that lets a domain move to another registrar. Porkbun's field for it is called **Auth Code** [S120].
- **DNS records** are the list of settings that tells the internet where the website is and where the email goes.
- **Nameservers** are the addresses that say which company holds a domain's DNS records.
- **DNSSEC** is a security seal on the DNS records. In the public record it shows as a DS record [S151].
- **Public record** (also called WHOIS) means the registration data of a domain, which anyone can look up [S28].

What happens, in short.

- The domain moves once, straight from Wix to Porkbun.
- Porkbun charges its transfer price and adds one year to the domain [S121] [S124]. For a .com name that is \$11.81 since 1 November 2026 [S140] [S141].
- Porkbun copies the DNS records it can find and holds the domain's DNS after the move [S121].
- When the move is done, Wix disconnects the Wix site from the domain [S35]. The same day your helper points the domain at the new site ([Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages)) and sets up the email forwarding ([Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail)).
- The Wix site plan, the old business email and the domain subscription at Wix end by themselves on 26 November 2026. Auto renew was off for all three when the Wix account was checked on 2 November 2026 ([Section 2](#the-end-dates)). Once the domain is at Porkbun, its renewals are managed there [S35]. Nothing has to be canceled at Wix.

One rule holds for the whole section. Do not change the contact details of the domain at Wix, not now and not during the move. Wix says that changing the contact information locks the domain for 60 days [S38] [S54]. The domain could then not move before it expires.

Start only when the new site is published at the preview address and you have checked every page there ([Section 1, Part 4](#part-4-your-helper-publishes-the-new-site-the-first-time)).

### The dates

The domain expires on 27 November 2026 at 01:04 UTC [S27]. UTC is the world's standard clock time. In New York that moment is 8:04 PM on Thursday 26 November 2026, Thanksgiving. So "Expires on Nov 26, 2026" on the Wix **Domains** page is the same moment. The Wix site plan and the business email end that same evening.

| When | Who | What | Where |
|---|---|---|---|
| By Thursday 5 November 2026 | Your helper | Turn off privacy and DNSSEC at Wix, then check the public record | [Part A](#part-a-turn-off-privacy-and-dnssec-at-wix) |
| Before Monday 9 November 2026 | Your helper | Open the Porkbun account and save the list of DNS records at Wix | [Part B](#part-b-get-porkbun-ready) |
| Monday 9 November 2026, at the latest Monday 16 November 2026 | Your helper | Start the transfer | [Part C](#part-c-start-the-transfer) |
| About 5 to 7 business days later | Porkbun | The transfer is done and Porkbun sends an email | [Part D](#part-d-while-the-transfer-runs) |
| The day the transfer is done | Your helper | Point the domain at the new site, then turn on the email forwarding | [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages) and [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) |
| As soon as the forwarding works, and no later than Friday 20 November 2026 | Gerta | Back up the old mailbox | [Section 2](#back-up-the-mailbox) |
| Thursday 26 November 2026, in the evening in New York | Nobody | The Wix site plan, the old business email and the domain subscription at Wix end by themselves | [Section 8](#8-what-cannot-be-undone) |

Why these dates.

- Porkbun says a transfer takes 5 to 7 business days [S120]. Wix says it usually takes up to 7 days [S35]. A transfer started on Monday 16 November 2026 may only be done on Wednesday 25 November 2026, the day before the domain expires. A later start leaves no time to fix a problem.
- Porkbun warns that the old registrar may block the transfer of an expired domain [S120].
- A transfer that is done before the domain expires adds one year. The domain then runs until 27 November 2027 [S121] [S124].
- Part A comes a few days before the transfer. That leaves time to check the public record and, if needed, to ask Wix Customer Care.

If the transfer cannot start by Monday 16 November 2026, use the backup plan under [If something goes wrong](#if-something-goes-wrong).

### Part A: Turn off privacy and DNSSEC at Wix

Do Part A by Thursday 5 November 2026.

**Why.** Porkbun recommends deleting DNSSEC records before a transfer, to prevent problems with the DNS [S125]. Wix sells DNSSEC only together with private registration, so one switch, **Privacy and DNSSEC protection**, turns off both [S53]. Wix also advises turning privacy off before a transfer, so that you do not miss emails about it [S35].

Know two things before you click.

- With the protection off, anyone can see the name and contact details of the domain's owner in the public record (WHOIS) [S53]. The domain is in your helper's name, so these are your helper's details. They stay visible until the move is done and Porkbun's free WHOIS privacy covers them [S121] [S137]. That is about one to three weeks. Your helper decides whether to accept that. If not, stop here and use the backup plan under [If something goes wrong](#if-something-goes-wrong), so that the domain does not expire.
- On the **Edit contact info** page, change nothing else and save nothing else. Changing the contact information locks the domain for 60 days [S38] [S54].

1. **Your helper signs in** to Wix and goes to **Domains** [S53].
2. Click the **Domain Actions** icon next to hairbygerta.com [S53].
3. Click **Edit contact info** [S53].
4. Read the email address shown for the registrant contact (the domain's owner). Wix sends the transfer code to that address [S35]. On 2 November 2026 it was the helper's personal email address. If your helper cannot open that mailbox, stop and ask Wix Customer Care. Do not change the address here. A change locks the domain for 60 days and has to be confirmed from both the old and the new address [S54].
5. At the bottom of the page, click **Show more** next to **Privacy and DNSSEC protection** [S53].
6. Click **Turn off protection** [S53].
7. Click **Turn Off Protection** to confirm [S53].
8. Leave the page without saving anything else.

Porkbun says DNSSEC can be turned on again there after the transfer [S125]. This guide does not use it.

**Check that the DS record is gone**

Wix's page does not say how soon the change reaches the public record [S53]. So your helper checks it before Part C. The check only reads. It changes nothing.

1. Open https://rdap.verisign.com/com/v1/domain/hairbygerta.com in Chrome or Microsoft Edge. This is the domain's record at Verisign, the registry (the organization that keeps the official list of all .com addresses) [S27]. It is a page of plain text. If the browser offers to save a file instead, cancel and use ICANN Lookup, as the end of this part says.
2. Press Ctrl + F and type `delegationSigned` [S92] [S93].
3. Read the word right after it. `true` means a DS record is still there, and a list called `dsData` follows with its details. `false` means the DS record is gone [S151]. On 2 November 2026 it said `true` [S27].
4. If it says `false`, go on with Part B.
5. If it still says `true`, wait a few hours and look again. Load the page fresh each time with Ctrl + Shift + R [S92] [S93].
6. If it still says `true` 48 hours after the protection was turned off, your helper asks Wix Customer Care to remove the DNSSEC record (the DS record) of hairbygerta.com.
7. Do not start Part C while it says `true`. If it still says `true` on Monday 16 November 2026, use the backup plan under [If something goes wrong](#if-something-goes-wrong).

If the Verisign page does not open, use ICANN Lookup at https://lookup.icann.org. Anyone can look up the current registration record of a domain there [S28]. Type hairbygerta.com and look for DNSSEC in the result. If you cannot tell from it whether the DS record is gone, ask Wix Customer Care.

### Part B: Get Porkbun ready

Do Part B before Monday 9 November 2026. It can be done on the same day as Part A.

1. Your helper opens an account at https://porkbun.com with the helper's personal email address. Do not use info@hairbygerta.com. The business email ends on 26 November 2026, and the email address of the account must keep working while the domain moves and every year after. Wix itself recommends a contact email address that is not tied to the domain [S54].
2. **Your helper signs in** to Porkbun and looks at the default contact details. Click **ACCOUNT**, then **Settings / Billing**. In the section **Registration Defaults**, under **Default Contacts**, click the pencil icon next to **REGISTRANT** [S150]. The details must be the helper's real name, address and phone number, with the helper's personal email address. Porkbun fills in the contacts of newly registered domains from these details [S150]. Its page does not say the same for a transferred domain, so [Part D](#part-d-while-the-transfer-runs) checks the domain's own contacts after the move.
3. Look at the price. Porkbun's price list shows a .com transfer at \$11.81 since 1 November 2026, with all fees included. Most transfers include a one year renewal [S140] [S141]. The price shows again on the screen in Part C.
4. **Your helper signs in** to Wix, goes to **Domains**, clicks the **Domain Actions** icon next to hairbygerta.com and then **Manage DNS Records** [S39].
5. Take a screenshot of the whole list. Keep it, but not in the `hairbygerta` folder, because everything in that folder is published. Porkbun copies the records it can find, but says its lookup cannot see every record, so they have to be checked after the move [S121]. Section 4 needs this list.
6. Keep time free for the day the transfer is done. Section 4 and then Section 5 have to be done that same day. Your helper signs in for both, so plan the day together. Porkbun gives 5 to 7 business days [S120]. For a start on Monday 9 November 2026 that is Monday 16 to Wednesday 18 November 2026. It can also come a few days sooner, because under ICANN's policy a transfer goes through when the old registrar does not answer within five calendar days [S41].
7. Before that day, Gerta decides whether the domain is also locked to the helper's GitHub account. See [Whose GitHub account this is, and what Gerta decides](#whose-github-account-this-is-and-what-gerta-decides) in Section 4.

On 2 November 2026 the list in Wix had these records.

| Type | Name | Value | Used for |
|---|---|---|---|
| A, three records | hairbygerta.com | addresses of Wix | the Wix site |
| CNAME | www | `cdn3.wixdns.net` | the Wix site |
| TXT | hairbygerta.com | `google-site-verification=cEwGkDfnBA3KDOjrEJ1VtYTp5NZwNkC0jiX1SQsjxsI` | Google Search Console |
| TXT | hairbygerta.com | `google-site-verification=NXMw3mRnshf6rlL9Zr3VDm7ZgP6b0F9xVxUJ2XmSpbQ` | Google Workspace, the business email |
| TXT | hairbygerta.com | `v=spf1 include:_spf.google.com ~all` | the business email |
| MX, five records | hairbygerta.com | Google's mail servers | the business email |

### Part C: Start the transfer

Do Part C on Monday 9 November 2026, and at the latest on Monday 16 November 2026. Start only when the check at the end of Part A says `false`.

**Get the code from Wix**

1. **Your helper signs in** to Wix and goes to **Domains** [S35].
2. Click the **Domain Actions** icon next to hairbygerta.com [S35].
3. Select **Transfer away from Wix** [S35].
4. Read the page and click **Transfer Domain** [S35].
5. Click **I Still Want to Transfer** [S35].
6. **Your helper signs in** to the mailbox of the helper's personal email address, the registrant contact email. Wix sends the authorization code there [S35]. Look in the spam folder too. Keep the code as private as a password. It works only once [S120]. Use it the same day.

**Order the transfer at Porkbun**

7. **Your helper signs in** to Porkbun and goes to https://porkbun.com/transfer, or clicks **TRANSFER** at the top of the page [S120].
8. In **Domain Name**, type `hairbygerta.com`, without www [S120] [S121].
9. In **Auth Code**, paste the code from step 6 [S120] [S121].
10. Click **Submit** [S120] [S121].
11. Leave these two boxes ticked [S120] [S121].
    - "Automatically turn on WHOIS privacy / data redaction after domains transfer in." It turns on Porkbun's free WHOIS privacy after the move, so your helper's details are hidden in the public record again [S121] [S137].
    - "Automatically enable auto renewal so your domains don't accidentally expire after they transfer in." Porkbun then renews the domain every year by itself. What that costs is in [Section 9](#9-yearly-cost-after-the-move).
12. Of the two DNS choices, choose "Move DNS to Porkbun after the transfer, without pausing anything." Porkbun then copies the DNS records it can find now, and puts the domain on Porkbun's DNS when the transfer is done [S121]. Do not choose "Pause my transfer until I've set up DNS here." That choice holds the transfer back until your helper says go, so that the records can be copied and the nameservers pointed at Porkbun first [S121]. This guide does not change the nameservers at Wix.
13. Click **Add Transfers to Cart** [S120] [S121].
14. The cart opens. If it shows the DNS choice again, check that it is still the one from step 12. Then click **Continue to Billing** [S120].
15. Read the price on the screen. For .com it is \$11.81 since 1 November 2026 [S141].
16. Your helper pays and finishes the order.

The transfer has now started. [Part D](#part-d-while-the-transfer-runs) shows how to follow it. If Porkbun refuses the code or says the domain is locked, see [If something goes wrong](#if-something-goes-wrong).

### Part D: While the transfer runs

Porkbun says a transfer takes 5 to 7 business days [S120] and sends an email when it is finished [S123]. Wix says up to 7 days [S35]. Under ICANN's policy, if the old registrar does not answer within five calendar days, the transfer goes through [S41].

**Follow the status**

1. **Your helper signs in** to Porkbun and clicks **Transfer** at the top. The **Domain Transfers** page opens [S122].
2. Read the status of hairbygerta.com and find it in the table below [S122].

| Status | What it means | What to do |
|---|---|---|
| pending transfer request | The transfer is queued and not fully sent yet. | Look again after a few minutes. |
| pending transfer from losing registrar | Porkbun waits for Wix. This is normal and can take 5 to 7 days. | Nothing. Wait. |
| pending owner confirmation | Porkbun has sent an email to the registrant contact, the helper's personal email address. | Open that email and follow its link. Look in the spam folder too. |
| bad authcode | The code was not accepted. | See [If something goes wrong](#if-something-goes-wrong). |
| domain status does not allow transfer | The domain is still locked at Wix. | See [If something goes wrong](#if-something-goes-wrong). |
| transfer complete | The move is done. The domain shows in **Domain Management** within minutes. | Go on with "The day the transfer is done" below. |

At Wix the transfer can show as pending or in progress. Wix says this is normal [S35]. While the move runs, the Status in Wix's Whois Lookup tool shows "pending transfer" [S35]. The Wix help page behind that marker links to the tool. Wix cannot follow a transfer once it has started, and says to ask the new registrar for news about it [S35]. Here that is Porkbun.

While the transfer runs, keep to three rules.

- If an email asks your helper to approve or confirm the transfer of hairbygerta.com, check that it comes from Wix or Porkbun and names hairbygerta.com. Then approve it.
- Change nothing at Wix, no contact details [S54] and no DNS records. Porkbun copied the records when the transfer was ordered [S121], so a later change at Wix does not reach Porkbun.
- Cancel nothing at Wix. The Wix site keeps running until the move is done [S35].

**The day the transfer is done**

Porkbun's email comes [S123], or the status says transfer complete [S122]. Three things are now true.

- Wix has disconnected the Wix site from the domain [S35]. hairbygerta.com may show no website until Section 4 is done.
- Porkbun puts the domain on its own DNS, because of the choice in Part C, step 12 [S121]. Section 4 checks this.
- The old business email keeps receiving mail only if Porkbun copied its MX records, the records that deliver the email [S35] [S121]. Section 5 replaces them with the records for the forwarding.

So go straight on to [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages) the same day, and then to [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail).

**In the 15 days after the transfer**

1. **Your helper signs in** to Porkbun. On **Domain Management**, click **Details** next to hairbygerta.com and look at the section **Contacts** [S150]. The details must be the helper's real name, address and phone number, with the helper's personal email address. If something is wrong, click the edit icon next to **Contacts**, correct it in the **DOMAIN CONTACTS** pop-up and click **Submit** [S150].
2. Porkbun turns on its free WHOIS privacy after the transfer, because the box stayed ticked in Part C [S121] [S137]. On **Domain Management**, the eye icon under **WHOIS**, to the right of the domain, offers **Redact Privacy Data**, **Use Privacy Service** and **Make Public** [S136]. Do not choose **Make Public**.
3. Watch the helper's personal inbox, spam folder included, for an email from Porkbun that asks to verify (confirm) the contact email address of the domain. Open the link in it at once. ICANN requires a registrar to check the email address or the phone number of the domain's owner within 15 days of a transfer. A registrar that gets no answer has to check by hand or suspend the domain [S55]. A suspended domain shows no website and receives no email. If no such email comes, there is nothing to do.

### If something goes wrong

**The code is refused.** Porkbun shows the status bad authcode [S122]. On the **Domain Transfers** page, check that the code there matches the code in Wix's email, letter by letter [S122]. To enter it again, click **Update authcode** under **Options**. This restarts the transfer [S122]. If the code is right and still refused, ask Wix Customer Care for a new code and enter it the same way [S122]. If it is still refused after that, contact Porkbun support [S122].

**The domain is still locked.** Porkbun shows the status domain status does not allow transfer. Porkbun says this usually means the domain was not unlocked at the old registrar [S122]. Wix says the domain must be unlocked before a transfer, but its guide shows no unlock button [S35]. So your helper asks Wix Customer Care to unlock hairbygerta.com for the transfer. ICANN's policy gives a registrar five calendar days to remove the lock and give out the code after the owner asks [S41] [S42].

To see the lock yourself, open the public record from [Part A](#part-a-turn-off-privacy-and-dnssec-at-wix) again, load it fresh with Ctrl + Shift + R and press Ctrl + F for `transfer prohibited` [S92] [S93]. While its status list says client transfer prohibited, the registry refuses a transfer [S27] [S152]. On 2 November 2026 it said so [S27]. When the words are gone, **your helper signs in** to Porkbun, clicks **Transfer** at the top and then **Update authcode** under **Options**. This sends the transfer again [S122].

The status can also say that the transfer has been submitted and rejected too many times. Porkbun has then tried 15 times without success. Check the lock and the code as above [S122], and ask Porkbun support if nothing moves.

If Wix says the domain is locked for 60 days, for example after a change of the contact details [S38] [S54], it cannot move before it expires. Use the backup plan below.

**The transfer is still running on Monday 23 November 2026.** Ask Wix Customer Care to speed it up. Porkbun says some registrars do this when asked, but not all [S120] [S122]. The domain expires in the evening of Thursday 26 November 2026, so also read the rules for an expired domain below.

**The backup plan, extending the domain at Wix.** Use it if the transfer has not started by Monday 16 November 2026, if the DS record of Part A is still there on that day, if your helper does not accept the public details of Part A, if the domain is locked for 60 days, or if the transfer fails and there is no time to start it again before the domain expires. Extend the domain at Wix before it expires [S105], and move it later.

1. **Your helper signs in** to Wix and goes to **Domains** [S105].
2. Click **Extend** next to hairbygerta.com [S105].
3. Choose one year and click **Continue** [S105].
4. Choose a privacy option and click **Continue** [S105]. If you choose one with DNSSEC, Part A has to be done again before the later move.
5. Enter the payment information and click **Submit Purchase** [S105].

Read the price on the screen before you click **Submit Purchase**. Wix says the price depends on the domain ending, the currency, the number of years, the privacy option and local taxes [S154]. On 2 November 2026 Wix showed about \$26 a year for this domain at its regular price, more than Porkbun's \$11.81 [S141]. Change nothing in the contact details while you do this. Wix says that would lock the domain from transfer for 60 days [S104]. Afterwards, check on the **Domains** page that the expiry date now says 2027. If a renewal payment fails, the domain still expires on the old date [S103].

What the backup plan means until the later move.

- The domain and its DNS records stay at Wix. A Wix domain can point to a site hosted elsewhere through its A and CNAME records [S39]. So your helper points it at the new site before 26 November 2026, when the Wix site plan ends. First do [Section 4, Part 2](#part-2-tell-github-the-domain). Then put GitHub's values from [Part 3](#part-3-switch-to-porkbuns-nameservers-and-add-the-records) into the records at Wix.
- The email forwarding of Section 5 is set up at Porkbun, from **Domain Management** [S132]. Porkbun moves a domain into that page when its transfer is complete [S122], so the forwarding has to wait for the move. After 26 November 2026 the old business email no longer receives mail [S31]. So until the move, mail to info@hairbygerta.com does not arrive. Decide with your helper before 26 November 2026 what to do about that. [Section 8, Part 3](#part-3-the-business-email-ends) says what ends with the business email.
- For the later move, do Parts A to D again.

**The domain expires before the move is done.** It expires on 27 November 2026 at 01:04 UTC, which is 8:04 PM on 26 November 2026 in New York [S27].

- Wix says an expired domain is no longer connected to its site [S101]. ICANN says the website and the email of an expired domain stop for a time [S102]. That hits the new site too.
- Wix says an expired domain can still be transferred during its grace period, about 30 days from the expiry date. In the redemption period that follows, a transfer is no longer possible [S104].
- If the transfer of an expired domain fails, the domain may go into the redemption period, and getting it back then costs \$100 [S104]. So Wix recommends extending an expired domain before starting a transfer [S104]. During the grace period that is **Extend Registration** in the banner under the domain on the **Domains** page [S101].
- Porkbun warns that the old registrar may block the transfer of an expired domain [S120]. Porkbun's transfer page says a transfer includes a one year renewal, unless the domain is inside the auto renew grace period [S121]. Its help page says no year is added when a domain expired, was renewed at the old registrar and is moved fewer than 45 days after the expiry date [S124]. So a transfer after the expiry date may add no year.

[Section 8, Part 2](#part-2-the-domain-expires) says what happens after that.

**Point the domain back to the Wix site.** This only works while the Wix site plan still runs, so only until the evening of 26 November 2026, because Wix needs an upgraded site to connect a domain [S57]. It sends visitors back to the Wix site. It does not move the registration back to Wix [S58].

Before the transfer is complete there is nothing to undo for the website. Wix disconnects the site only once the domain has been transferred [S35]. If you give up the move, your helper can switch **Privacy and DNSSEC protection** back on at any time with **Turn On Protection** [S53].

After the domain has moved to Porkbun, do these steps.

1. **Your helper signs in** to Wix, goes to **Domains** and clicks **Add an Existing Domain** [S57].
2. Click **Connect a domain you already own** [S57].
3. Select the site and click **Continue** [S57].
4. Type hairbygerta.com and click the arrow [S57].
5. Click **connect it to your site** [S57]. If a **Start Transfer** option appears, do not click it. Click **connect your domain** in the sentence below it [S57].
6. Click **go to our manual setup** [S57].
7. Click **Start** [S57].
8. Click **pointing** [S57].
9. Click **Switch to Pointing Instructions** [S57]. Wix opens a step by step outline. Leave it open [S57].
10. In a new tab, **your helper signs in** to Porkbun. On **Domain Management**, click **Details** next to hairbygerta.com, then the edit icon next to **DNS Records**. The **Manage DNS Records** page opens [S129].
11. Back in the Wix outline, click **I logged in** [S57].
12. Click **I found my domain settings** [S57].
13. Click **I found the records** [S57]. Wix now gives you its A record and its CNAME record (the two settings that say where the website is) [S57].
14. At Porkbun, find an A record whose **Host** is empty (the domain itself, without www). Click the pencil icon on it, put the value Wix shows into **Answer** and click the save button [S129] [S130]. If there is no such record, click **Add Record**, choose the **Type** A, leave **Host** empty, put the value into **Answer** and click **Add** [S129] [S130].
15. Do the same for the CNAME record whose **Host** is www [S129] [S130].
16. Delete every other A, AAAA or CNAME record for the domain itself and for www, and every record that points to pixie.porkbun.com. For each one, click the trash can icon, then **OK** [S129] [S131]. Wix says to replace your records with its own, not to add to them [S57].
17. Back in the Wix outline, click **I updated my records** [S57].
18. Wait up to 48 hours [S57].

Wix's page lists the A record 185.230.63.107 and the CNAME www to pointing.wixdns.net. Trust the values on your own Wix screen [S57]. Wix does not support DNSSEC for a domain connected this way [S57]. So check that the **Porkbun DNSSEC** switch under **Details** is off [S142].

These records only count while the domain uses Porkbun's nameservers. [Section 4, Part 3](#part-3-switch-to-porkbuns-nameservers-and-add-the-records) shows how to check that. If the domain was already pointed at the new site, also take the domain out of GitHub afterwards, as the steps under [How to undo the switch](#how-to-undo-the-switch) in Section 4 show.

**The website and the email stop some days after the move.** Look first for the verification email of [Part D](#part-d-while-the-transfer-runs), in the spam folder too. A registrar that gets no answer can suspend the domain [S55].

## 4. After the transfer: pointing the domain at GitHub Pages

This is the switch. When it is done, www.hairbygerta.com shows the new site from GitHub. Your helper sets the domain in GitHub and changes a few records at Porkbun, both in the helper's own accounts. Gerta makes one decision beforehand and looks at the result. The work takes about half an hour, then you wait. The switch itself changes nothing in Wix and nothing in the `hairbygerta` folder on your computer.

"The transfer" in the title is the move of the domain from Wix to Porkbun in [Section 3](#3-moving-the-domain-from-wix-to-porkbun-step-by-step). Do this section on the day that move is finished. Read it once before the transfer starts, so that Gerta can make her decision in time.

Words used in this section.

- **DNS records** are the list of settings that tells the internet where the website is and where the email goes. After the transfer this list is at Porkbun.
- **Nameservers** say which company holds a domain's DNS records. Porkbun's own nameservers have names that end in `.ns.porkbun.com` [S127].
- An **A record** points a name at the number address of a server, an IPv4 address. An **AAAA record** does the same with the newer kind of address, an IPv6 address [S130].
- A **CNAME record** points a name at another full name [S130].
- A **TXT record** holds a line of text. It is mostly used to prove who owns a domain [S130].
- **Host** and **Answer** are the two main fields of a record at Porkbun. The Host is the part of the name in front of hairbygerta.com, for example `www`. An empty Host means hairbygerta.com itself. The Answer is the content of the record, for example the address it points to [S130].
- **HTTPS** is the secure form of a web address, the one that starts with https://.
- The **security certificate** is the proof behind HTTPS. GitHub requests one for your domain by itself [S62].
- The **repository** is the project on GitHub that holds the site files [S63].

### Whose GitHub account this is, and what Gerta decides

The new site is in the GitHub account achooStorm. That account belongs to your helper, not to Gerta. In plain words, this means four things.

- **The helper does every step at GitHub and at Porkbun.** Only a person with admin rights for the repository can set the domain at GitHub [S64]. The Porkbun account is the one your helper opened in [Section 3, Part B](#part-b-get-porkbun-ready). Gerta cannot do these steps alone, and she needs the helper again for every later change in either place.
- **The domain is in the helper's name.** Your helper is the registrant, the person listed as the domain's owner. So the helper changes the records at Porkbun, today and later.
- **The site files are in the helper's account.** Ask your helper for a copy of the folder `hairbygerta` and keep it, so that the site can be published from another account if the two of you ever stop working together.
- **Gerta decides about verifying the domain.** GitHub recommends verifying the domain [S64]. That is the optional lock at the end of this section. Verifying ties hairbygerta.com to the helper's GitHub account. From then on only repositories owned by that account may publish a GitHub Pages site at hairbygerta.com or at a name directly under it, such as www.hairbygerta.com [S66]. This protects the address from strangers [S66]. It also ties the address of Gerta's business, on GitHub, to an account that is not hers. The TXT record that keeps the domain verified sits in the domain's DNS records, so at Porkbun, in the helper's account [S66]. GitHub's page does not say how a verification is taken off again [S66]. Whether to do this is Gerta's decision alone. The helper verifies the domain only after Gerta has clearly said yes.

### Before you start the switch

- The transfer in Section 3 is finished. Porkbun sends an email when it is done [S123], and hairbygerta.com then shows on the **Domain Management** page at Porkbun [S122]. See [Section 3, Part D](#part-d-while-the-transfer-runs).
- The new site looks right at the preview address https://achoostorm.github.io/hairbygerta/.
- Your helper is there to sign in to GitHub and to Porkbun, and has the pictures of the Wix DNS records from [Section 3, Part B](#part-b-get-porkbun-ready).
- Gerta has decided about the lock, yes or no. If she said yes before the transfer started, your helper may have done the lock then. See [the optional lock](#optional-lock-the-domain-to-the-github-account) at the end of this section.
- You do this on the day the transfer is finished, without waiting for a quiet day. Wix disconnects the Wix site from the domain once the domain has been transferred away [S35], so the address may show no website until this section is done. The secure address can take up to an hour to start working [S65].
- The email forwarding in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) comes straight after Part 3 of this section, on the same day.

### Part 1: Save a copy of today's DNS records

You need this copy if a record is deleted by mistake, here or in Section 5. It also shows what Porkbun copied from Wix. Porkbun copies the records it can find when the transfer is ordered, and says to check them afterwards, because a lookup cannot see every record [S121].

On 2 November 2026 the Wix account showed these records for hairbygerta.com.

| Type | Name | Value | What it is for | What happens to it |
|---|---|---|---|---|
| A, three records | hairbygerta.com | the addresses of the Wix site | the Wix site | deleted in Part 3 |
| CNAME | www | `cdn3.wixdns.net` | the Wix site | deleted in Part 3 |
| TXT | hairbygerta.com | `google-site-verification=cEwGkDfnBA3KDOjrEJ1VtYTp5NZwNkC0jiX1SQsjxsI` | Google Search Console | stays |
| TXT | hairbygerta.com | `google-site-verification=NXMw3mRnshf6rlL9Zr3VDm7ZgP6b0F9xVxUJ2XmSpbQ` | Google Workspace, the business email | stays |
| TXT | hairbygerta.com | `v=spf1 include:_spf.google.com ~all` | the business email | Section 5 |
| MX, five records | hairbygerta.com | Google's mail servers | the business email | Section 5 |

If the lock was done at Wix before the transfer, the list at Wix also had the GitHub TXT record. Its name starts with `_github-pages-challenge-`. It stays.

1. **Your helper signs in** to Porkbun and goes to **Domain Management**. If that page does not open by itself, click **ACCOUNT** at the top right and choose **Domain Management** [S127].
2. Click **Details** next to hairbygerta.com [S127].
3. Click the edit icon next to **DNS Records**. The **Manage DNS Records** page opens with the list of records [S129].
4. Change nothing yet. Take a screenshot or a phone photo of the whole list.
5. Compare the list with the table above. Write down every TXT or MX record that is missing. Part 3 adds a missing verification record. The email records are handled in Section 5.
6. Keep the pictures together with the pictures of the Wix list. Do not save them in the `hairbygerta` folder, because everything in that folder is published.

### Part 2: Tell GitHub the domain

GitHub says to do this before the DNS records change. Otherwise someone else could host a site on one of your names in between [S64].

1. **Your helper signs in** to github.com with their account achooStorm.
2. Open https://github.com/achooStorm/hairbygerta.
3. Under the repository name, click **Settings**. If you cannot see it, open the dropdown menu with the three dots at the end of that row and click **Settings** there [S64].
4. In the sidebar, in the section "Code, planning, and automation", click **Pages** [S64].
5. Under "Custom domain", type `www.hairbygerta.com`, with www at the front [S64].
6. Click **Save** [S64].

Why www. With www.hairbygerta.com as the custom domain and the records of Part 3 in place for both names, GitHub sends visitors of hairbygerta.com on to www.hairbygerta.com by itself [S64]. The pages of the new site already give https://www.hairbygerta.com/ as their address.

Two things happen now.

- GitHub starts a DNS check [S62]. It cannot pass yet, because the records do not point to GitHub yet. If GitHub shows a warning now, carry on with Part 3.
- GitHub adds a small file named CNAME to the repository, because the site is published from a branch [S64]. Never delete it, or the site stops showing at the domain [S65]. Before the next upload from the `hairbygerta` folder, pull first (pull means fetching GitHub's latest version into the folder), so that the folder has that file too [S64]. [Section 6, Part A](#part-a-get-the-latest-version) shows how.

### Part 3: Switch to Porkbun's nameservers and add the records

GitHub says to remove a default record that the DNS provider set [S64]. Extra records, or records that do not point to GitHub, can stop the security certificate [S62]. Porkbun's advice is the same. Delete its parking records and the records of the old host before you add your own [S131].

**Check the nameservers**

1. **Your helper signs in** to Porkbun and goes to **Domain Management**, as in Part 1 [S127].
2. Click **Details** next to hairbygerta.com and look at the nameservers [S127].
3. They should be `curitiba.ns.porkbun.com`, `fortaleza.ns.porkbun.com`, `maceio.ns.porkbun.com` and `salvador.ns.porkbun.com` [S127]. The choice "Move DNS to Porkbun after the transfer, without pausing anything." in Section 3 puts the domain on Porkbun's DNS when the transfer is done [S121]. If you see these four names, go on with step 7.
4. If you see other names, for example `ns2.wixdns.net` and `ns3.wixdns.net`, click the edit icon next to the nameservers [S127]. Porkbun does not change the nameservers of a domain on its own when the domain moves in [S126].
5. Click **Use Our Default Nameservers** [S127].
6. Click **Save Nameservers**. If Porkbun asks for it, click **Submit** once more [S127] [S128]. The change can take up to 48 hours. Most places see it within a few hours [S127].

**Delete the old website records**

Do steps 7 to 19 in one go, without a break. Between deleting and adding, the address shows no website.

7. Under **Details**, click the edit icon next to **DNS Records**. The **Manage DNS Records** page opens [S129].
8. Find a record whose Answer is `pixie.porkbun.com`. Porkbun's own default records point there and show its parking page [S131]. If there is none, go on with step 11.
9. Click the trash can icon beside that record, then click **OK** [S129].
10. Repeat steps 8 and 9 until no record with `pixie.porkbun.com` is left [S131].
11. Delete the old Wix website records the same way. These are the three A records for hairbygerta.com itself and the CNAME record for www with the Answer `cdn3.wixdns.net` [S131].
12. Look through the list once more. No record of the Type A, AAAA, ALIAS or CNAME may be left for hairbygerta.com itself or for www. Delete any that is left [S62] [S131]. Also delete a record of one of these types whose Host is `*`, if there is one. Such a record stands for every name under the domain, and GitHub strongly advises against it [S64].

Leave every other record alone, above all the MX and TXT records. The email records are handled in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail). They are the MX records and the TXT record that starts with `v=spf1`. The TXT records whose Answer starts with `google-site-verification=` stay as they are, and so does a TXT record whose Host starts with `_github-pages-challenge-`.

**Add the new records**

13. Click **Add Record** [S129].
14. In **Type**, choose the type of the first row of the table below. For an A record the list shows **A - Address record** [S130]. For the other rows, choose the entry for the type in the table.
15. Fill in **Host** from the same row. Where the table says leave empty, leave the field empty [S130].
16. Fill in **Answer** from the same row. The name of this field changes with the type. For an A record it is called **IPv4 Address** [S130].
17. Leave **TTL** as it is. **Notes** can stay empty [S130].
18. Click **Add** [S129] [S130].
19. Click **Back** and check that the new record is in the list [S129]. Then do steps 13 to 19 again for the next row, until every row that applies is done.

These are the records, in the fields of Porkbun's form [S130].

| Type | Host | Answer | Add it? |
|---|---|---|---|
| A | leave empty | `185.199.108.153` | yes |
| A | leave empty | `185.199.109.153` | yes |
| A | leave empty | `185.199.110.153` | yes |
| A | leave empty | `185.199.111.153` | yes |
| AAAA | leave empty | `2606:50c0:8000::153` | yes |
| AAAA | leave empty | `2606:50c0:8001::153` | yes |
| AAAA | leave empty | `2606:50c0:8002::153` | yes |
| AAAA | leave empty | `2606:50c0:8003::153` | yes |
| CNAME | `www` | `achoostorm.github.io` | yes |
| TXT | leave empty | `google-site-verification=cEwGkDfnBA3KDOjrEJ1VtYTp5NZwNkC0jiX1SQsjxsI` | only if it is not in the list yet |
| TXT | leave empty | `google-site-verification=NXMw3mRnshf6rlL9Zr3VDm7ZgP6b0F9xVxUJ2XmSpbQ` | only if it is not in the list yet |
| TXT | the name GitHub gave, without `.hairbygerta.com` at the end | the value GitHub gave | only if the lock was done at Wix before the transfer and the record is not in the list yet |

- The four A and the four AAAA addresses are GitHub's own. They were checked against GitHub's help page on 2 November 2026 [S64]. Check them there again on the day you do this.
- The CNAME answer is `achoostorm.github.io` and nothing more. Do not add `/hairbygerta` [S64].
- If Porkbun says that a CNAME or ALIAS record with that host already exists, an old record is still there. Delete it as in step 9, then add the row again [S131].
- The first Google TXT record keeps the site verified in Google Search Console. Google checks from time to time that its record is still there, and says not to remove it [S155]. The home page of the new site carries the same code. The second Google TXT record belongs to the business email. Keep both.
- The last row keeps the lock in place, if the lock was done at Wix before the transfer. GitHub says the TXT record must stay for the domain to stay verified [S66]. If the lock is still to be done, skip this row. The lock adds the record itself, after Part 4.

When you are done, hairbygerta.com itself has the four A and the four AAAA records of the table, www has the one CNAME record, and the TXT and MX records are still there. Then go on with Part 4. While GitHub checks, your helper can already set up the email forwarding in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail).

### Part 4: Wait for the check, then turn on HTTPS

1. In GitHub, go back to **Settings**, then **Pages** [S64]. If GitHub asks you to sign in again, the helper does it, as in Part 2.
2. Reload the page from time to time until a check mark shows beside `www.hairbygerta.com` [S62].
3. Under "GitHub Pages", select (tick) **Enforce HTTPS** [S62]. From then on everyone is sent to the secure address [S62]. If you cannot select it yet, wait and try again later. It can take up to 24 hours before this option is available [S64].

If there is still no check mark after an hour, restart the check [S62]. GitHub says this can be needed after DNS records were changed [S65].

1. Click **Remove** next to the custom domain [S62].
2. Type `www.hairbygerta.com` again.
3. Click **Save** [S62].

If Part 3 had to switch the nameservers, the check can take longer. See [How long it takes](#how-long-it-takes).

When the check mark shows, go through [What you see when it has worked](#what-you-see-when-it-has-worked). Its last part tells Google about the pages of the new site. If Gerta said yes to the lock and it was not done before the transfer, do [the lock](#optional-lock-the-domain-to-the-github-account) on the same day.

### How long it takes

- **The records at Porkbun.** GitHub says DNS changes can take up to 24 hours [S64].
- **The nameservers**, only if Part 3 had to switch them. Up to 48 hours. Most places see the change within a few hours [S127].
- **The secure address.** Up to an hour after the domain is set [S65].
- **The Enforce HTTPS option.** Up to 24 hours before you can select it [S64].
- **The lock**, if you do it. Up to 24 hours [S66].

If your own browser still shows an old page, clear its cache (the copies of pages it keeps) and look again [S65].

### What you see when it has worked

- In GitHub under **Settings**, **Pages**, a check mark shows beside www.hairbygerta.com [S62], and **Enforce HTTPS** is selected. This is the check to trust.
- https://www.hairbygerta.com opens the new site. It has its own look since 12 November 2026. You can tell it by the Call button at the top right and by the strip of five hair colors under the first photos.
- hairbygerta.com without www jumps to www.hairbygerta.com by itself [S64].
- The old page addresses still open, for example https://www.hairbygerta.com/gallery/ and https://www.hairbygerta.com/book-online/.
- If you still see an old page or a parking page, clear your browser's cache and look again [S65].

**The last step of the switch, telling Google about the new pages**

When all of the above is true, give Google the list of the site's pages. That list is the file sitemap.xml.

1. Open https://www.hairbygerta.com/sitemap.xml in the browser. It must show a list of page addresses that all start with https://www.hairbygerta.com/. Google says to make sure first that the sitemap can be reached [S143].
2. **Your helper signs in** to Google Search Console with the Google account that is an owner of the site there. Only an owner can submit a sitemap [S143]. If that owner account is Gerta's, **Gerta signs in** instead.
3. Go to https://search.google.com/search-console/sitemaps. That is where the link **Open the Sitemaps report** on Google's help page leads [S143].
4. If Search Console asks for a property (its word for a site), choose the one named hairbygerta.com or the one that starts with https://www.hairbygerta.com. Google warns against mixing up www and non-www properties [S143].
5. In **Add a new sitemap**, enter the address `https://www.hairbygerta.com/sitemap.xml` [S143]. If part of the address is already written in front of the box, do not type that part again. Use this address exactly, with https and www. The report goes by the exact address you submit and does not follow redirects [S143].
6. Click **Submit** [S143].
7. Look at the status later. **Success** means that Google has read the file. **Has errors** or **Couldn't fetch** means that something is wrong [S143]. Then click the row in the report to see what is wrong [S143]. Open the address from step 1 again, fix the problem with your helper and submit again [S143].

If the list already shows this address from the Wix site, submit it anyway. Google suggests submitting a sitemap again after big changes to it [S143]. If neither of you is an owner in Search Console, skip steps 2 to 7. The file robots.txt of the new site already names the sitemap, and that is Google's way for people without owner permission [S143].

### If it has not worked after 24 hours

- If Part 3 had to switch the nameservers, allow up to 48 hours in all [S127]. Then go through this list.
- Compare the **Manage DNS Records** page with the table in Part 3. Check the Type and the Answer letter by letter, and that each record is for hairbygerta.com itself or for www, as the table says. Delete any other record of the Type A, AAAA, ALIAS or CNAME for hairbygerta.com itself or for www [S62] [S131]. Then restart the check as in Part 4.
- A parking page shows, or a record still has the Answer `pixie.porkbun.com`. Delete that record [S131]. Then restart the check as in Part 4.
- **Details** does not show the four Porkbun nameservers. Switch them as in Part 3, steps 4 to 6 [S127].
- The list has records of the Type CAA (they name who may issue certificates for the domain). At least one of them must contain `letsencrypt.org` [S65]. If there are none, there is nothing to do.
- GitHub says the domain is already taken. The optional lock below frees the domain for the helper's account [S65] [S66]. It is still Gerta's decision.
- The address does not open at all on several devices, and the email stops too. Look at the public record as at the end of [Section 3, Part A](#part-a-turn-off-privacy-and-dnssec-at-wix). If `delegationSigned` still says `true`, an old DNSSEC record from Wix is left. Porkbun recommends deleting DNSSEC records before a transfer, because they can cause DNS problems [S125]. Your helper asks Porkbun's support to remove it.
- Nothing helps and the Wix site plan still runs. Then you can put the Wix site back for now, as under [How to undo the switch](#how-to-undo-the-switch).

### How to undo the switch

This puts the Wix site back on the domain. Wix only connects a domain to a site that is upgraded [S57]. So it only works while the Wix site plan still runs, until the evening of 26 November 2026, New York time ([The end dates](#the-end-dates) in Section 2). After that, it would first need a new site plan [S24]. See [Section 8, Part 1](#part-1-the-wix-site-plan-ends). Wix says the change can take up to 48 hours [S57], so decide early.

The domain stays registered at Porkbun. Connecting it to the Wix site does not move it back to Wix [S58].

1. Do the steps under "Point the domain back to the Wix site" in Section 3, [If something goes wrong](#if-something-goes-wrong). They connect the domain to the Wix site again. At Porkbun they change the website records to the values Wix shows and delete the rest of the records that Part 3 added for GitHub [S57].
2. For the website records, the values on your Wix screen count, not the old records in your pictures from Part 1 [S57]. Leave the TXT and MX records as they are. The email forwarding needs the MX records that point to Porkbun [S132].
3. **Your helper signs in** to GitHub, opens the repository and goes to **Settings**, then **Pages** [S64].
4. Under "Custom domain", the helper clicks **Remove** [S64]. Do this last. GitHub warns that DNS records pointing at GitHub with no domain set there could let someone else put a site on your name [S64].
5. Wait. Wix says it may take up to 48 hours [S57].

The pages of the Wix site and the `hairbygerta` folder on your computer were never changed, so there is nothing else to undo.

### Optional: lock the domain to the GitHub account

This is called verifying the domain. It stops other GitHub users from taking over your domain for a site of their own [S66]. It also ties hairbygerta.com to your helper's GitHub account achooStorm, because that is the account that verifies it [S66]. Do it only if Gerta has said yes. What she decides is explained under [Whose GitHub account this is, and what Gerta decides](#whose-github-account-this-is-and-what-gerta-decides).

**When to do it.** GitHub recommends verifying the domain before it is set in Part 2 [S64]. So if Gerta says yes before the transfer starts, your helper does the lock at Wix before Part C of Section 3 starts the transfer. Not later, because Porkbun copies the records when the transfer is ordered [S121], and Section 3 changes nothing at Wix while the transfer runs. Verifying can take up to 24 hours [S66], and that wait is then over before the day of the switch. The record has to stay for the domain to stay verified [S66], but Porkbun's copy of the records can miss it [S121]. So Part 3 makes sure it is at Porkbun too, in the last row of its table.

If the lock was not done before the transfer, do it straight after Part 4, on the same day, with the record at Porkbun. Do not hold up Parts 2 to 4 for it, because the address may show no website until they are done [S35]. Only if GitHub says in Part 2 that the domain is already taken, do the lock before you go on [S65].

Your helper does every step, in GitHub and in the account that holds the domain's DNS records.

1. **Your helper signs in** to github.com with their account achooStorm and clicks the profile picture in the upper-right corner [S66].
2. Click **Settings**. These are the profile settings of the helper's account, not the repository settings [S66].
3. In the sidebar, under "Code, planning, and automation", click **Pages** [S66].
4. Click **Add a domain** [S66].
5. Type `hairbygerta.com` under "What domain would you like to add?" [S66].
6. Select **Add domain** [S66].
7. Leave this page open. Under "Add a DNS TXT record" it shows a name and a value [S66]. The name starts with `_github-pages-challenge-` and ends with `.hairbygerta.com` [S66]. Write both down or take a screenshot, because Part 3 may need them again. Do not save them in the `hairbygerta` folder.
8. Add the record in a new tab, where the domain's DNS records are on that day.
   - Before the transfer, at Wix. **Your helper signs in** to Wix, goes to **Domains**, clicks the **Domain Actions** icon next to hairbygerta.com and selects **Manage DNS Records** [S156]. In the **TXT (Text)** section, click **+ Add Record** [S156]. In **Host Name**, type the name from GitHub without `.hairbygerta.com` at the end. Wix says to leave this field blank for @, the domain itself [S156]. So, as at Porkbun, the field takes only the part in front of the domain. In **Value**, paste the value from GitHub [S156]. Click **Save** [S156].
   - After the transfer, at Porkbun. **Your helper signs in** to Porkbun and opens the **Manage DNS Records** page, as in Part 3, steps 1, 2 and 7 [S129]. Click **Add Record** [S129]. In **Type**, choose TXT. In **Host**, type the name from GitHub without `.hairbygerta.com` at the end, because the Host is only the part in front of the domain [S130]. In **Answer**, paste the value from GitHub [S130]. Click **Add** [S129].
9. Back on GitHub, click **Verify** [S66]. The DNS change can take up to 24 hours [S66]. If you left the page in the meantime, open the three-dot menu to the right of the domain and click **Continue verifying** first [S66]. If it still fails after 24 hours, compare the record with GitHub's name and value, letter by letter.
10. Keep that TXT record for as long as the domain should stay verified. It is what keeps the domain verified [S66]. If you added it at Wix, it has to be at Porkbun too after the transfer. That is the last row of the table in Part 3.

## 5. Free email forwarding from info@hairbygerta.com to Gmail

Porkbun's free email forwarding takes the mail sent to info@hairbygerta.com and passes it on to Gerta's Gmail address [S132]. It is not a mailbox. It only receives mail and passes it on [S135].

**When.** On the same day the transfer in [Section 3](#3-moving-the-domain-from-wix-to-porkbun-step-by-step) completes, straight after [Section 4, Part 3](#part-3-switch-to-porkbuns-nameservers-and-add-the-records). Wix says the business email stops working once the domain has moved away, until the domain's mail records (MX records) are added again [S35]. Until this section is done, mail for info@hairbygerta.com may not arrive anywhere.

**Why you need it.** The form on the Contact page of the new site does not deliver messages by itself. It opens the visitor's own email app with a message to info@hairbygerta.com. The email links on the site do the same. The old business email ends by itself on the evening of Thursday 26 November 2026, New York time (see [The end dates](#the-end-dates)). After that the old mailbox can no longer receive mail [S31]. From then on, mail for info@hairbygerta.com reaches Gerta only through this forwarding.

**Words used in this section**

- **DNS records** are the list of settings that tells the internet where the website is and where the email goes.
- An **MX record** is a DNS record that says which mail servers receive the domain's mail.
- A **TXT record** is a DNS record that holds one line of text.
- The **SPF record** is the TXT record that starts with `v=spf1`. Mail systems read it to check which servers may send mail for the domain.
- **Host** is the field on Porkbun's DNS page for the part in front of the domain name. Left empty, the record is for the domain itself, hairbygerta.com [S130].
- A **forward** is one address that passes its mail on, here info@hairbygerta.com to Gerta's Gmail address [S132].

### Before you turn on forwarding

- The transfer in Section 3 is complete. Porkbun sends an email when it is finished [S123], and hairbygerta.com then shows on the **Domain Management** page [S122].
- Your helper has done [Section 4, Part 3](#part-3-switch-to-porkbuns-nameservers-and-add-the-records). There the helper makes sure the domain uses Porkbun's nameservers. The records at Porkbun only work while it does [S126] [S127]. You do not have to wait for Section 4, Part 4.
- The Porkbun account is the helper's, so your helper does Parts 1 and 2. Gerta does Part 3 and the last backup.
- Gerta tells the helper which Gmail address the mail should go to. It is an inbox she can open.
- info@hairbygerta.com is the only address ending in @hairbygerta.com that Gerta uses. Porkbun has no catch-all that forwards every address of the domain [S132]. If there is another address, tell your helper. It needs its own forward, made as in Part 1.
- Gerta knows that the forwarding only receives mail, and that her replies go out from her Gmail address [S132].
- Two other ways are not part of this plan. Porkbun sells hosted email at \$3 a month per address, billed yearly [S135]. Through Wix Customer Care the Google Workspace mailbox can be moved from Wix to Google, and that cannot be undone [S160].

One thing changes in Part 2. Before the move, the mail for info@hairbygerta.com went to the old business email, the Google Workspace mailbox from Wix [S20]. The forwarding needs the domain's MX records to point to Porkbun [S132], and Porkbun says to delete the other MX records [S134]. So once Part 2 takes effect, new mail goes to Gerta's Gmail address and no longer to the old mailbox.

Do Part 1 and Part 2 in one sitting.

### Part 1: Create the forward at Porkbun

1. **Your helper signs in** to Porkbun. The **Domain Management** page opens. If the helper was already signed in, click **ACCOUNT** at the top right and choose **Domain Management** [S132].
2. Find hairbygerta.com and click the envelope icon in the **EMAIL** column [S132]. The **Email Hosting and Forwarding** page opens [S132].
3. Go to the section **Porkbun Email Forwarding** [S132].
4. Under **Create a New Forwarding Address**, type `info` as the username, the part in front of the @ [S132].
5. As the destination, type Gerta's Gmail address [S132]. Check it with Gerta letter by letter.
6. Click **Create Email Forward** [S132].
7. The page loads again and shows the new forward under **Current Forwards** [S132].

The forwards are free [S132]. If a screen asks for payment, stop and check that you are in the section **Porkbun Email Forwarding**.

### Part 2: The DNS records for forwarding

The forwarding needs these three records on the domain itself [S133].

| Type | Host | Answer | Priority |
|---|---|---|---|
| MX | leave empty | `fwd1.porkbun.com` | 10 |
| MX | leave empty | `fwd2.porkbun.com` | 20 |
| TXT | leave empty | `v=spf1 include:_spf.porkbun.com ~all` | none |

The old Google mail records have to go first. On 2 November 2026 the DNS records at Wix held five Google MX records and the SPF record `v=spf1 include:_spf.google.com ~all`. They may have come along to Porkbun with the domain [S121]. Do steps 1 to 7 without a break.

1. **Your helper signs in** to Porkbun and goes to **Domain Management** [S132]. Click **Details** next to hairbygerta.com, then the edit icon next to **DNS Records**. The **Manage DNS Records** page opens [S129].
2. Delete every MX record whose answer contains `google.com`. If they came along, there are five. To delete a record, click the trash can icon to the right of it, then **OK** [S129]. Porkbun says to delete the domain's other MX records [S134].
3. Delete the TXT record `v=spf1 include:_spf.google.com ~all` the same way [S129]. A domain may have only one SPF record [S134]. Porkbun's own SPF record comes in step 5.
4. Leave every other record as it is. That includes the two TXT records that start with `google-site-verification=` and the website records from Section 4. The verification records are not mail records.
5. Open the **Email Hosting and Forwarding** page again (Part 1, step 2). Click **Fix DNS** at the bottom of the page [S133]. Porkbun offers this button for MX records that were deleted or that point to a mail provider you no longer use [S133].
6. Open the **Manage DNS Records** page again (step 1) and compare it with the table. For the domain itself it must show each of the three records once, no other MX record, and only one TXT record that starts with `v=spf1` [S133] [S134]. Delete any extra one as in step 2. The two `google-site-verification=` records must still be there. If one is missing, see [For your helper](#for-your-helper).
7. If one of the three is missing, or if there was no **Fix DNS** button, add it by hand. Click **Add Record** [S129]. Choose the **Type**, leave **Host** empty, and type the answer from the table into **Answer**. For an MX record also type the **Priority** from the table [S130] [S133]. Leave **TTL** as it is and **Notes** empty [S130]. Click **Add** [S129] [S130].
8. Take a screenshot of the list. Do not save it in the `hairbygerta` folder.

### Part 3: Test the forwarding

1. Ask a friend to send an email to info@hairbygerta.com from the friend's own address, not from Gerta's Gmail address. Porkbun says to test from an address that is different from the one the mail is forwarded to [S132].
2. **Gerta signs in** to her Gmail and looks for the email in the inbox and in the spam folder.
3. Gerta replies. Ask the friend which address the reply came from. It is Gerta's Gmail address, not info@hairbygerta.com [S132].
4. Once www.hairbygerta.com shows the new site, test the form of the new site the same way (see [What you see when it has worked](#what-you-see-when-it-has-worked) in Section 4). The friend opens https://www.hairbygerta.com/contact/, fills in the form and clicks **Send**. Their email app opens with a message to info@hairbygerta.com. They send it, and Gerta checks her Gmail.

**If nothing arrives**

- Wait and test again later. If the nameservers were changed in Section 4 today, that change can take up to 48 hours. Most finish within a few hours [S127].
- **Gerta signs in** at gmail.com with info@hairbygerta.com [S33] and looks in the old mailbox too. A change of MX records takes some time to be recognized across the internet [S161]. Until then, mail still goes to the previous mail provider [S162].
- Your helper checks that the forward is listed under **Current Forwards**, with Gerta's Gmail address spelled right [S132].
- Your helper checks the records again as in Part 2, step 6 [S133] [S134].
- If it still does not work the next day, your helper asks Porkbun's support.

**The last backup.** When the test has worked, Gerta makes the last backup of the old mailbox, at the latest on Friday 20 November 2026. The steps are in [Back up the mailbox](#back-up-the-mailbox) in Section 2. New mail now goes to Gmail, so this backup holds all the mail the old mailbox received up to the switch. If the forwarding does not work by Friday 20 November 2026, do not wait for it. Make the backup on that day anyway.

Until the evening of 26 November 2026, Gerta also looks into the old mailbox now and then. For a while after Part 2, some mail can still arrive there [S161] [S162]. If she finds a new email there, she forwards it to her Gmail address by hand. After that evening she can no longer read the old mailbox [S31].

On Friday 27 November 2026, the day after the old mailbox has ended, test once more as in steps 1 and 2.

### Limits of the forwarding

- **It only receives.** Gerta's replies go out from her Gmail address, and the client sees that address [S132] [S135]. It helps to sign replies with the business name.
- **No catch-all.** Only an address with its own forward is passed on [S132]. Mail to any other address at hairbygerta.com does not reach Gerta.
- **Up to 20 forwards.** Porkbun allows up to 20 free forwards per domain [S132]. One forward can also go to more than one address [S132].
- **No old mail.** The forwarding passes on the mail it receives [S135]. It does not bring the old mail to Gmail. The old mail is in the backup.
- **It needs the MX records.** It works only while the domain's MX records point to Porkbun [S132]. If anyone changes them later, for example for another mail provider, the forwarding stops.
- **It needs the domain.** If the domain expires, its email is cut off too [S102]. So the yearly renewal matters ([Section 9](#the-domain-the-one-bill)).

### For your helper

- Email does not depend on GitHub. If the GitHub steps of Section 4 have to wait, still check the nameservers as in Section 4, Part 3, and do this section on the day the transfer completes.
- On 2 November 2026 the DNS records at Wix held five Google MX records, the SPF record `v=spf1 include:_spf.google.com ~all` and two TXT records that start with `google-site-verification=`. Section 3 chooses "Move DNS to Porkbun after the transfer, without pausing anything." With that choice Porkbun copies the records its lookup can find, and it puts the domain on Porkbun DNS when the transfer is done. The lookup cannot see every record [S121]. So on the day, the list may hold the Google records, Porkbun's forwarding records, both or neither. Part 2 works in each case.
- The goal for the domain itself (empty **Host**) is MX `fwd1.porkbun.com` priority 10, MX `fwd2.porkbun.com` priority 20 and TXT `v=spf1 include:_spf.porkbun.com ~all` [S133]. There is no other MX record and no second `v=spf1` record [S133] [S134]. Next to them stay the website records from [Section 4, Part 3](#part-3-switch-to-porkbuns-nameservers-and-add-the-records), the GitHub verification TXT record if the domain was verified, and the two Google verification TXT records.
- The two Google verification records are `google-site-verification=cEwGkDfnBA3KDOjrEJ1VtYTp5NZwNkC0jiX1SQsjxsI` (Google Search Console) and `google-site-verification=NXMw3mRnshf6rlL9Zr3VDm7ZgP6b0F9xVxUJ2XmSpbQ` (Google Workspace). If one is missing, add it as Type TXT with an empty **Host** [S130].
- Porkbun's page does not say whether **Fix DNS** removes other MX or SPF records [S133]. That is why Part 2 deletes the Google records first and checks the list afterwards. For records added by hand, Porkbun says to remove the existing MX and SPF records first [S133].
- A domain may have only one SPF record, and Porkbun shows how two senders are merged into one [S134]. The plan needs no Google part, because Gerta replies from Gmail. Only if she must still send from the old mailbox before it ends, use `v=spf1 include:_spf.porkbun.com include:_spf.google.com ~all` [S134]. Take the Google part out again after 26 November 2026.
- To send the mail back to the old mailbox before it ends, delete Porkbun's two MX records. Then add Google's MX record with an empty **Host**, the answer `smtp.google.com` and priority 1. Google gives this as its MX value today, and says the older values that start with `aspmx` are still supported [S161]. Then put the old SPF record `v=spf1 include:_spf.google.com ~all` back in place of Porkbun's. Wix says the business email needs its MX records after a transfer [S35]. The forwarding stops then [S132], and the old mailbox ends anyway on the evening of 26 November 2026 [S31].
- Never write Gerta's Gmail address into this guide or anywhere else in the repository. The repository is public.

## 6. How to replace a placeholder with a real photo

A placeholder is a stand-in file, a beige picture with a faint logo. It holds the spot of a photo that could not move with you from Wix. The site does not show it. The spot shows on its page as soon as your own photo is in. This section shows how to put your own photo in such a spot and publish it. Start with one spot. If the computer steps are new to you, do them together with your helper.

Publishing goes through the GitHub account achooStorm, which belongs to your helper. So Gerta cannot publish a photo alone. She chooses the photos and can do Parts B to D. Part E is done by the helper, or by the two together on a computer where the helper has signed in.

You need the computer that has the folder `hairbygerta`. It also needs Python (the free program that builds the pages) and GitHub Desktop (GitHub's free program for sending changes to GitHub). The steps are written for Windows. The new site must already be published ([Section 1, Part 4](#part-4-your-helper-publishes-the-new-site-the-first-time)).

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

A cloned folder has no guard against Wix-only photos yet. The guard is a check that runs with every commit, but only where it was switched on [S82]. Your helper switches it on with one command, once after the repository is created (Section 1, Part 4 does that) and once after every clone: type `python tools/licensing_check.py --install-hook` in the black window (Command Prompt) opened in the folder. Do not copy the guard file by hand. Until then, type `python tools/licensing_check.py` there before Part E, and go on only when it answers `Photo licensing check passed`.

### The quick way, for the helper

The script `tools/add_photo.py` does Parts B and C below and the build of Part D in one step. Do Part A first. Keep the original photos outside the folder `hairbygerta`, for example in a folder `new-photos` next to it. In a terminal in the folder `hairbygerta`:

1. `..\hairbygerta-env\venv\Scripts\python.exe tools\add_photo.py --list` shows the 26 places that still wait for a photo.
2. `..\hairbygerta-env\venv\Scripts\python.exe tools\add_photo.py ..\new-photos\IMG_0001.jpg g05 --alt "Long brunette waves, seen from the back"` puts that photo in the place `g05`. Add `--dry-run` first to see what would happen.
3. The script turns the photo upright, makes the two sizes and a smaller WebP copy of each, removes the place and date the phone saved in the photo, writes the alt text and builds the pages.
4. Look at the page as in Part D, then publish with Part E. The commit holds more files than the list in step 30, because of the WebP copies.

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
7. Crop it to a tall shape, 9 wide to 16 high, like a phone photo held upright.
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

If you do not see your photo, hold Ctrl and Shift and press R. That loads the page fresh, without the copy the browser kept [S92] [S93].

#### Part E: Publish

29. Open GitHub Desktop. The **Changes** tab on the left lists every file that changed [S82].
30. Check the list. For this example it holds these six files: `images/g05.jpg`, `images/sm/g05.jpg`, `tools/build_pages.py`, `content/gallery.json`, `gallery/index.html` and `image-manifest.json`. The last one is the site's list of all pictures. The build in step 23 wrote your photo into it by itself, with the status `owner-photo`. Never edit that file by hand. If one of the six is missing, a step of Part B or Part C was skipped. Go back to step 23 and read its lines.
31. In the **Summary** field, type a short note, for example `Real photo for g05` [S82].
32. Under the Description field, click the button that starts with **Commit** and ends with **to main**. GitHub's help page calls it **Commit to BRANCH** [S82]. The program puts the number of files into the name, so for this example it reads **Commit 6 files to main** [S86].
33. Click **Push origin** [S82]. This sends the commit to GitHub [S83]. GitHub then publishes the change to the site by itself [S94].
34. Wait up to 10 minutes [S3].
35. Open https://achoostorm.github.io/hairbygerta/gallery/ and check the photo. Once the domain points to the new site, use https://www.hairbygerta.com/gallery/. Hold Ctrl and Shift and press R if you do not see your photo.

If the list in step 30 shows more files, look at each one before you commit. Other `index.html` files and `404.html` that the build wrote again are fine. After New Year all ten change once, because the build puts the year into the footer of every page. A picture or a zip file that you did not put there yourself is not fine. Take it out of the folder first.

For several photos, do Parts B and C for each one. Then do Parts D and E once.

For your helper: the full test of the site is `qa/run_all.py`. Its first lines say how to start it. A run takes about two minutes. After a photo is replaced, its part `qa/licensing_check.py` lists the photo in the class `owner-photo`, so that a person can look at each one. A file that is an exact copy of a Wix-only photo stays a `LICENSING MATCH`, whatever `image-manifest.json` says. Exit code 2 means a licensing match: do not commit.

### Which name is used where

A name can be used on more than one page. Do steps 17 to 21 in every content file listed for the name. Look at every one of those pages in Part D.

| File names | Content files (in `hairbygerta/content`) |
|---|---|
| `g01` `g02` `g04` `g05` `g06` `g07` `g15` `g20` `g21` | `gallery.json` |
| `g14` `g16` `g17` `g18` `g19` | `gallery.json` |
| `g10` | `gallery.json`, `about.json` |
| `brunette-balayage` `copper-waves` | `gallery.json`, `about.json` |
| `foils-highlights` `makeup-red-lips` | `home.json`, `gallery.json` |
| `home-styling` `home-smile` `home-waves` `meet-extensions` | `home.json` |
| `about-salon` | `about.json` |
| `svc-haircut` `svc-bridal` | no page (the Services page shows no photos since 12 November 2026) |

`home.json` is the Home page, `gallery.json` the Gallery page and `about.json` the About page. Every page shows a photo in a tall frame and cuts it to fit, so keep the hair or the face near the middle. In the Gallery a click on a photo opens the whole photo.

Every spot is tall, 9 wide to 16 high, whatever shape the placeholder file has. Crop your photo to that tall shape in step 7, not to the shape of the placeholder. A wide photo would be cut hard at the sides.

The two real photos on the site, `g12` and `g13`, are not in this table, because they are not placeholders. To change one of them, ask your helper: each has two more copies in another file format that have to be changed with it.

To see the size of a placeholder, right-click it, choose **Properties** and open the **Details** tab. The line Dimensions shows it.

### If something goes wrong with a photo

- Step 23 prints a line that starts with WARNING: a step was forgotten, and the line says which one. The name was deleted from the list but a file is still the placeholder picture, or the photo was saved but its name is still in the list, or only one of the two files was replaced, or the description after `"alt"` is still empty. Do what the line says and do step 23 again.
- Step 23 prints a line that starts with ERROR, or shows the word SyntaxError or Traceback: the message names a file. If it is a picture, it is not a JPG file. Save your photo again as JPG under that name. If it is `tools/build_pages.py` or a file in `content`, most likely a quotation mark or a comma got lost in Part C. In GitHub Desktop, right-click that file in the list of changed files and click **Discard changes** [S82] [S86]. In the "Confirm Discard Changes" window, click **Discard Changes** again [S82]. Then do the edit once more.
- GitHub Desktop does not commit and shows `PHOTO LICENSING CHECK: STOP`: the folder has a guard that runs with every commit [S82]. It names a file that must not be published: a file with the same content as one of the 26 Wix-only photos, or a zip file. Save a photo of your own over that file. Or put the placeholder back: right-click the file in the list of changed files and click **Discard changes** [S82] [S86]. Take a file out of the folder only when it is an extra file that the site never had. Then commit again.
- When the guard stops a commit, GitHub Desktop shows the guard's message and offers the button **Commit anyway** [S95]. Never click **Commit anyway** and never choose **Bypass Commit Hooks**. Both commit the file without the check [S82] [S95]. The same holds when the message starts with `PHOTO LICENSING CHECK: COULD NOT RUN` or says that Python 3 was not found: stop and ask your helper.
- The guard only recognises an exact, unchanged copy of a Wix-only file. A Wix photo that was cropped, resized or saved again is not recognised. So a commit that goes through is no proof that a photo may be used. The rule under [Which photos you may use](#which-photos-you-may-use) decides [S4] [S5].
- You want the placeholder back after publishing: in GitHub Desktop click **History** in the left sidebar, right-click your commit and click **Revert Changes in Commit** [S84]. This takes back everything in that commit, so every photo you published with it. If you made other commits after it, ask your helper first: GitHub says to revert from newest to oldest, otherwise you may see merge conflicts (changes that do not fit together) [S84]. Then click **Push origin** [S82]. The photo is off the site, but it stays in the history of the repository [S84].

## 7. Booking by phone

Every **Call 347-671-5095** button on the new site calls the number, and every **Text Gerta** link starts a text message to it. A Call button is at the top of every page, and on a phone one stays at the bottom of the screen. The Home page, the Services page and the About page have a Call button and a Text Gerta link of their own. There is no online booking link to paste and nothing to set up. [Section 1, Part 3](#part-3-booking-stays-by-phone) says why.

If the phone number ever changes, tell your helper. The site is in the helper's GitHub account, so the helper makes the change, in three places in the folder `hairbygerta`.

- In several files in the folder `content`. Search all of them for the old number, 347-671-5095.
- In `js/site.js`, on the line with `var phoneHref`. No button uses that line today, but keep it in step with the number.
- In `seo/jsonld-home.json`, which gives the number to search engines.

The helper first gets the latest version as in [Section 6, Part A](#part-a-get-the-latest-version). After the change the helper builds the pages as in [Part D](#part-d-build-the-pages-and-look) of that section, steps 22 and 23, and publishes them as in [Part E](#part-e-publish), steps 29 to 34. In step 30 the list of changed files is then not the one of the photo example. It shows the files the helper changed and the pages that the build wrote again. `README.md` in the folder lists the same three places.

If you ever get an online booking link for the site, ask your helper. `README.md` says where it goes.

## 8. What cannot be undone

Four things in this move are hard or impossible to undo. Two of them are final, losing the domain after it expires and closing the Wix account. The other two, the site plan and the mailbox, can only be bought again once they have ended. For each of the four, this section says what it means for you and the one thing to do first.

Nothing has to be canceled. On 2 November 2026 auto renew was already off for the Wix site plan, the domain at Wix and the business email. All three end by themselves on the evening of Thursday 26 November 2026, New York time. That day is Thanksgiving, so plan no step for that day. The dates and how to see them again are in [The end dates](#the-end-dates) in Section 2.

### Part 1: The Wix site plan ends

**What happens on 26 November 2026.** The Wix site plan (Core) ends with its paid period, because auto renew is off [S59]. The Wix site is not deleted and keeps its content [S19]. But from then on it has a free Wix address and shows Wix ads [S19]. A site plan that has ended cannot be switched back on. Someone would have to buy a new one [S24].

If the transfer in Section 3 is complete by then, the Wix site is no longer on hairbygerta.com anyway. Wix disconnects the Wix site from the domain when the domain has been transferred away from Wix [S35]. Once [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages) is done, hairbygerta.com shows the new site.

**The one thing to do first.** After Section 4, have your helper confirm that hairbygerta.com shows the new site. Do it by Tuesday 24 November 2026 at the latest. A browser can show an old copy of a page, so do not judge by eye alone. The checks are in Section 4 under [What you see when it has worked](#what-you-see-when-it-has-worked). If something is wrong, follow [If it has not worked after 24 hours](#if-it-has-not-worked-after-24-hours) in Section 4.

If the new site still cannot be shown, Gerta and your helper can decide to keep the Wix site for one more year as a fallback. **Your helper signs in** to Wix and clicks **Turn Auto Renew On** under the plan on the **Premium Subscriptions** page. This works only before the plan ends [S24]. It costs one more year of Core, \$348 at the price seen on 2 November 2026, and Wix does not refund renewals [S19]. The plan alone does not bring the Wix site back to hairbygerta.com, because Wix disconnected the site when the domain left [S35]. The domain then also has to be pointed back at the Wix site, as in [How to undo the switch](#how-to-undo-the-switch) in Section 4.

### Part 2: The domain expires

The domain is the address hairbygerta.com. It is registered at Wix until 27 November 2026 at 01:04 UTC [S27]. UTC is the world's standard clock time. In New York that moment is 8:04 PM on Thursday 26 November 2026. Auto renew is off, so Wix does not renew it [S45].

**What happens on 26 November 2026.** If the transfer to Porkbun in [Section 3](#3-moving-the-domain-from-wix-to-porkbun-step-by-step) is complete, nothing happens. The domain is then registered at Porkbun and no longer at Wix [S35] [S122]. In most cases Porkbun adds one year to a transfer, and the time that was left is not lost [S121] [S124]. So the domain then runs until November 2027. Check the new expiry date in the public record at https://lookup.icann.org [S28]. From then on the domain renews at Porkbun. What that costs is in [Section 9](#9-yearly-cost-after-the-move).

If the domain is still at Wix that evening, it expires. This is the case to avoid.

- An expired domain is no longer connected to a site [S101]. ICANN (the organization that sets the rules for domain names) says the website and the email of an expired name are cut off for a time, as a last warning [S102]. That would stop the new site and the email forwarding too.
- **About the first 30 days (the Grace Period).** The domain can still be extended at Wix at no extra fee. On the **Domains** page, click **Extend Registration** in the banner under the domain [S101]. Wix says it can also still be transferred in this time, but recommends extending it first, because a failed transfer attempt can push it into the Redemption Period [S104]. In the last 10 days of the Grace Period the domain may be auctioned privately [S101]. So only about 20 days are safe.
- **About 30 days more (the Redemption Period).** The domain can no longer be transferred [S104]. Getting it back costs a fee. Two Wix pages say \$100 [S103] [S104]. Another says the fee varies and is shown on the **Domains** page [S101]. You click **Keep Domain** in the banner under the domain. Wix says this is not guaranteed and can take up to 7 days [S101].
- **After that (Pending Delete).** The domain cannot be retrieved any more. 5 to 10 days later anyone can register it, and you have no claim to it [S101].

If someone else buys the name, every link, Google result and business card with hairbygerta.com leads to them.

**The one thing to do first.** Turn off privacy and DNSSEC by Thursday 5 November 2026, as in [Section 3, Part A](#part-a-turn-off-privacy-and-dnssec-at-wix). Then start the transfer on Monday 9 November 2026, and no later than Monday 16 November 2026. Porkbun says a transfer usually takes five to seven days [S123], and Wix says up to 7 days [S35]. Porkbun also says a transfer can be refused when the domain has expired or is about to expire [S120]. So do not leave it to the last week. While it runs, follow it as in [Section 3, Part D](#part-d-while-the-transfer-runs). If a transfer has started but is still not complete on Monday 23 November 2026, read [If something goes wrong](#if-something-goes-wrong) in Section 3 with your helper that same day.

**The backup plan.** If the transfer cannot start by Monday 16 November 2026, extend the domain at Wix for one more year before it expires, and move it to Porkbun later [S105]. On 2 November 2026 Wix showed about \$26 a year for this domain at its regular price. Wix does not refund domain payments [S45]. Gerta and your helper decide on this payment together.

1. **Your helper signs in** to Wix and goes to **Domains** [S105].
2. Click **Extend** next to hairbygerta.com [S105].
3. Choose a registration period of one year and click **Continue** [S105].
4. Select a privacy option and click **Continue** [S105]. Wix sells DNSSEC only together with private registration [S53]. If you choose an option with DNSSEC, do [Section 3, Part A](#part-a-turn-off-privacy-and-dnssec-at-wix) again before the later transfer. Porkbun recommends deleting DNSSEC records before a transfer [S125].
5. Enter the payment information and click **Submit Purchase** [S105].

Change nothing in the contact details while you do this. Wix says that would lock the domain from transfer for 60 days [S104]. Afterwards open the **Domains** page and check that the expiry date now says 2027 [S25].

When to move it after an extension. Porkbun adds no year to a transfer made fewer than 45 days after the day the domain expired, or fewer than five days after it was renewed [S124]. To be safe, count from the old expiry date and start the transfer no earlier than Monday 11 January 2027. That is 45 days after 27 November 2026. Otherwise you may pay twice for the same year.

What the backup plan means for the rest. The site plan and the business email still end on 26 November 2026. Until the later transfer, the domain's settings stay at Wix. Your helper can point the domain at the new site from inside Wix, by its A and CNAME records [S39]. The GitHub steps and values are in [Section 4](#4-after-the-transfer-pointing-the-domain-at-github-pages). Section 5 is written for a domain that is already at Porkbun, so ask your helper how mail for info@hairbygerta.com is received in between. After 26 November 2026 the business email no longer receives it [S31], unless it is kept (Part 3).

### Part 3: The business email ends

The business email is the mailbox info@hairbygerta.com. It is a Google Workspace mailbox that Wix sells [S20]. Gerta is its administrator.

**What happens on 26 November 2026.** The mailbox ends with its paid period, because auto renew is off [S30]. After that nobody can read, receive or send email in it [S31]. Wix says the old mail is kept only as long as Google's rules allow, and comes back only if the business email is bought again within that time. Wix gives no number of days [S31]. Google's own page, for customers who buy from Google directly, says the data is deleted after a cancellation and cannot be restored [S106]. So count on the old mail being gone on 26 November 2026.

New mail does not stop. From the day the forwarding in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) works, mail for info@hairbygerta.com goes through Porkbun to Gerta's Gmail address [S132]. Replies then go out from that Gmail address, not from info@hairbygerta.com [S132]. If Gerta wants a mailbox that also sends as info@hairbygerta.com, she decides that before 26 November 2026. Section 5 names the other ways.

**The one thing to do first.** Back up the whole mailbox with Google Takeout [S32], after the forwarding works and by Friday 20 November 2026. The steps are in [Back up the mailbox](#back-up-the-mailbox) in Section 2. A copy only holds the mail that was there when you asked for it [S32].

Until the end of the paid period the mailbox can still be switched back on. **Your helper signs in** to Wix, goes to **Premium Subscriptions**, clicks the **More Actions** icon next to the business email, then **Turn auto renew on** [S30]. Wix showed \$84 a year for it on 2 November 2026, and a business email bought through Wix is not refunded [S30]. Do this only if Gerta has decided to keep the mailbox, and ask your helper first. The domain's mail can go to the mailbox or to the forwarding, not to both. Wix says the business email only works after a transfer if its MX records are added again [S35]. The forwarding needs Porkbun's MX records in their place [S132] [S134].

### Part 4: The 14 Shutterstock photos

**What it means for you.** You bought these 14 photos inside Wix. Wix's rules: they cannot be downloaded, and they may be used only on Wix, not with other website services [S4]. So they can never move to the new site. They stay usable on any site in the same Wix account [S4]. On the new site a placeholder (a beige box with a faint logo) stands in for each one.

The same goes for 12 more photos from the old site. Eleven came free with Wix or its template, and Wix allows those within Wix only [S5]. For one there is no proof of a license (the permission that says where a photo may be used). That makes 26 placeholders.

The step with no way back is closing the Wix account: you lose access to the account and everything in it [S107].

**The one thing to do first.** Never close the Wix account while hairbygerta.com is still registered at Wix, while the business email is still in use, or while you may still need the Wix site. Closing cannot be undone, and you lose access to everything in the account [S107]. Wix lets you close it as soon as auto renew is off, without waiting for the domain or the plans to end [S19] [S107]. So close it only after the domain has completely finished moving to its new registrar, the mailbox is backed up and the forwarding works, and you are sure you will never want the Wix site or those photos again. There is no hurry: the account can stay open for free once the paid subscriptions are canceled [S107].

For the new site, use photos of your own: see [Section 1, Part 2](#part-2-collect-your-own-photos). Never save or screenshot a photo from the Wix site.

## 9. Yearly cost after the move

Prices change, so read each price again on the day you pay.

After the move you pay one bill a year, for the domain (the address hairbygerta.com) at Porkbun. Everything else is free.

| What | Where | Cost per year |
|---|---|---|
| Domain hairbygerta.com | Porkbun | \$11.81, the .com price since 1 November 2026, all fees included [S140] [S141] |
| Website | GitHub Pages | \$0 [S2] [S108] |
| Domain settings (DNS) | Porkbun | \$0 [S165] |
| Email forwarding for info@hairbygerta.com | Porkbun | \$0 [S132] |
| **Total** | | **\$11.81 a year at the price of 1 November 2026** |

**Not in the total**

- The transfer in November 2026. It costs \$11.81 once and adds one year to the domain [S121] [S141]. So it pays for the first year, and the first renewal at Porkbun comes in November 2027. The steps are in [Section 3](#3-moving-the-domain-from-wix-to-porkbun-step-by-step).
- Price rises. Porkbun expects the .com price to rise by about 7% a year until 2030 [S140]. If it rises by 7% before November 2027, that renewal costs about \$12.64.
- Tax. Porkbun's prices include ICANN fees and any other fees [S141]. Its price page says nothing about tax. So read the total on the payment screen before you pay.
- A mailbox that can also send mail as info@hairbygerta.com. Forwarding only receives mail and passes it on [S135]. Porkbun's hosted email costs \$3 a month per address, billed yearly [S135]. [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail) names the other ways.
- The backup plan. If the domain has to be extended at Wix first, as in [Section 8, Part 2](#part-2-the-domain-expires), that year costs about \$26 at Wix, and the move to Porkbun comes later.

### The domain: the one bill

- A registrar is the company where a domain is registered and renewed. After the move that is Porkbun.
- Porkbun's price for a .com domain is \$11.81 a year for registration, for renewal and for a transfer, with ICANN fees and any other fees included [S141]. ICANN is the organization that sets the rules for domain names. The price went up to \$11.81 on 1 November 2026 [S140].
- Porkbun expects the .com price to rise by about 7% every year from 2026 until 2030 [S140]. So the renewal can cost a little more each year.
- Porkbun says it sends an email each time renewal prices go up across the whole domain industry [S139].

**Auto renew**

With auto renew on, Porkbun renews the domain by itself as the expiry date comes near. Porkbun's help page says this happens when auto renew is on for the domain and a credit card is on file in the Porkbun account [S166]. The transfer in Section 3 keeps the auto renew box ticked, so auto renew starts on [S121].

- Porkbun charges the renewal at its price of that day, which can be higher than the year before [S168].
- Renewal payments are final and not refunded [S168].
- If the payment fails and nobody fixes it, the domain expires [S168].
- Porkbun sends a reminder about 1 month and again 1 week before the expiry date, to the main email address of the domain's owner [S168]. The domain is registered in the helper's name, so the helper watches for these emails.

To see or change auto renew, follow these steps.

1. **Your helper signs in** to porkbun.com. The **Domain Management** page opens. If it does not, click **ACCOUNT** at the top right and select **Domain Management** [S138].
2. Find hairbygerta.com. Look at the icon in the **Renew** column, to the right of the domain [S138].
3. A white icon means auto renew is off [S138]. To turn it on, click the icon, then **Enable Auto Renew** [S138]. Do not click **Disable Auto Renew**.
4. To check the card on file, click **ACCOUNT** at the top right and select **Settings / Billing**. The card is shown under **Billing Information** [S167].

Porkbun does not say how many days before the expiry date the renewal is made [S166] [S168]. So check the domain yourself once a year, as below.

**Where to see the renewal price**

1. **Your helper signs in** to porkbun.com and opens **Domain Management** [S139].
2. Click **Details** at the far right of the row of hairbygerta.com [S139].
3. Read the **Renewal Price**. It is the domain's current yearly renewal price [S139].

Porkbun lists the current price of every domain ending at https://porkbun.com/products/domains [S141].

**Once a year, in September**

The domain expires in late November. Each September, check these two things.

- The **Renewal Price**, as above [S139].
- That auto renew is on and the card on file is still valid [S138] [S166] [S167].

After the renewal, the public record at https://lookup.icann.org shows the new expiry date, one year later [S28]. If it still shows the old date in the week before the expiry date, renew by hand as below.

To renew by hand, for example when auto renew is off, follow these steps.

1. **Your helper signs in** to porkbun.com and opens **Domain Management** [S166].
2. Click the icon in the **Renew** column next to hairbygerta.com [S166].
3. Under **Manual Renewals**, keep the **Domain** box ticked [S166].
4. Click **Add Renewals to Cart** [S166].
5. Read the price in the cart, then click **Continue to Billing** and pay [S166].

ICANN says that when a domain expires, its website and its email are cut off, and getting it back can cost an extra fee [S102]. Porkbun sends one more notice 5 days after a domain has expired [S168]. Do not wait for it.

### GitHub Pages: free

- Hosting means keeping the site's files on a computer that shows them to visitors. GitHub Pages does this for a public repository (a project on GitHub that anyone can view) on the GitHub Free plan [S108]. GitHub Free costs \$0 [S2].
- GitHub Pages supports using your own domain [S70].
- Limits. A site may be no larger than 1 GB, and there is a soft limit of 100 GB of data sent to visitors per month [S108]. The `hairbygerta` folder is a few megabytes.
- One thing to know. GitHub says Pages may not be used as free hosting to run an online business or an online shop, or for a site that is mainly there to handle sales [S108]. The new site only shows information. It sells nothing and takes no payment. Clients book by phone or through the salon. The page does not say how GitHub judges a small information site like this one. If GitHub ever writes about it, the message goes to your helper, because the GitHub account is theirs. Ask your helper to tell you at once. Moving the folder to another host could then add a cost.

### Porkbun DNS and email forwarding: free

- DNS records are the list of settings that tells the internet where the website is and where the email goes. After the move they are kept at Porkbun. Porkbun says it offers DNS management for your domain for free [S165].
- Email forwarding passes mail for info@hairbygerta.com on to Gerta's Gmail address, as set up in [Section 5](#5-free-email-forwarding-from-infohairbygertacom-to-gmail). Porkbun gives up to 20 forwarding addresses per domain for free [S132].
- Forwarding only receives mail. Replies go out from Gerta's Gmail address [S132] [S135].
- Nothing else at Porkbun is needed. If a Porkbun screen asks you to pay for anything other than the domain, stop and ask your helper.

### What you pay Wix today: look it up

On 2 November 2026 the Wix account showed these renewal prices. Auto renew was off on all three, so none of them is renewed after 26 November 2026.

| What | Renewal price per year at Wix | Auto renew |
|---|---|---|
| Site plan Core | \$348 | Off |
| Domain hairbygerta.com | about \$26, Wix's regular price | Off |
| Business email info@hairbygerta.com (Google Workspace) | \$84 | Off |
| **Total** | **about \$458** | |

At these prices the move saves about \$446 a year, about \$458 at Wix minus \$11.81 at Porkbun. The amounts really paid can differ, so check them on the invoices. You only look and change nothing.

1. **Your helper signs in** to Wix.
2. Go to the **Billing History** page at https://www.wix.com/account/billing-history [S113].
3. Use the **All Dates** drop-down to find the charges of the last 12 months [S114].
4. Click the **More Actions** icon next to a charge [S113].
5. Click **View Invoice** [S113].
6. Write down the total and what it was for.
7. Do steps 4 to 6 for every charge of the last 12 months.
8. Add the totals up.

The Billing History page holds the invoices for everything paid at Wix [S114]. Look for the site plan, the domain and the business email. Two services with the same renewal date can share one invoice [S114]. If more than one year was paid at once, look further back and divide that charge by the number of years.

With auto renew off on all three, nothing more is paid to Wix after 26 November 2026. The Wix account itself can stay open for free [S107]. Before you ever close it, read [Section 8, Part 4](#part-4-the-14-shutterstock-photos).

## Official help pages used

The pages from [S120] on, most of them pages of Porkbun, were opened on 2 November 2026. The pages with lower numbers were first opened on 12 or 13 October 2026. Some of them were opened again on 2 November 2026, for example the public record [S27] and Wix's pages on moving a domain away [S35] and on DNSSEC [S53]. Each entry gives the page title, its address and what it confirms. A page keeps its number when the guide changes, so the numbers do not follow the order of the sections. A missing number belongs to a page that this guide no longer uses, or was never used. An entry marked as a public record is a lookup of the domain's own data, not a help page. One entry is the program text of GitHub Desktop, for three things that no help page shows. A few entries are help pages of Google and Microsoft, for example for Google Takeout and for the reload keys of their browsers.

- [S1] GitHub Docs, "What is GitHub Pages?". https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages Confirms: the address form of a project site: `http(s)://<owner>.github.io/<repositoryname>`.
- [S2] GitHub, "Plans & pricing for every developer and team". https://github.com/pricing Confirms: the Free plan costs \$0 per user per month.
- [S3] GitHub Docs, "Creating a GitHub Pages site". https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site Confirms: GitHub Pages sites are publicly available on the internet; a change can take up to 10 minutes to publish after it is pushed; GitHub's own next check point is after an hour; with GitHub Free the repository of the site must be public; Visit site under "GitHub Pages"; a site published from a branch needs a push by someone with admin permissions and a verified email address.
- [S4] Wix Help Center, "Using Shutterstock Media Purchased Through Wix". https://support.wix.com/en/article/using-shutterstock-media-purchased-through-wix Confirms: Shutterstock files bought through Wix are not downloadable; they may only be used in websites and content on Wix, not with other website or content services; they are usable on any site in the same Wix account.
- [S5] Wix Help Center, "Wix Media: Adding Free Media from Wix". https://support.wix.com/en/article/wix-media-adding-free-media-from-wix Confirms: the free Wix media in the Media Manager and on the template is for digital use within Wix only.
- [S6] Wix Help Center, "Avoiding Copyright Infringement: Images". https://support.wix.com/en/article/avoiding-copyright-infringement-images Confirms: free Wix images may not be used anywhere outside Wix; for a stock image you bought, check which license you purchased and its restrictions.
- [S19] Wix Help Center, "Canceling a Wix Premium or Studio Plan". https://support.wix.com/en/article/canceling-a-wix-premium-plan Confirms: a canceled plan stays active until the end of the subscription period; after that the site stays online with its content, on the free Wix address and with Wix ads; the expiration date is on the Premium Subscriptions page; a plan may renew up to 3 weeks before its expiration date; no refunds for renewals; domain and business email are not canceled with the plan; the steps More Actions, Cancel Plan, Cancel Now; a plan canceled in its first 14 days ends immediately; once auto renew is off the account can be closed without waiting.
- [S20] Wix Help Center, "Business Email: An Overview". https://support.wix.com/en/article/business-email-an-overview Confirms: Wix business email is Google Workspace; the Business Email page (manage.wix.com/account/mailboxes) shows the business emails you own.
- [S21] Wix Help Center, "Viewing Your Site Plans and Other Subscriptions". https://support.wix.com/en/article/viewing-your-premium-plans Confirms: plans and other Wix purchases are listed on the Premium Subscriptions page; the View Subscriptions link; the wrong-account note and the account email locator.
- [S22] Wix Help Center, "Checking Your Upcoming Renewals for Premium or Studio Plans". https://support.wix.com/en/article/checking-your-upcoming-renewals-for-premium-plans Confirms: plans renew automatically at the end of the subscription period; the Upcoming payment column shows the date of the next renewal payment; the Info icon; the date can differ from the expiration date when auto renew is off.
- [S24] Wix Help Center, "Reactivating a Canceled Premium or Studio Site Plan". https://support.wix.com/en/article/reactivating-a-canceled-premium-plan Confirms: Turn Auto Renew On on the Premium Subscriptions page reactivates a canceled plan before it ends; after it has ended you have to buy a new plan.
- [S25] Wix Help Center, "Accessing Your Domains Page". https://support.wix.com/en/article/accessing-your-domains-page Confirms: user panel, Account Settings, Domains; the Assigned Domains section; the Domains page shows the expiry and payment renewal dates.
- [S27] Verisign (the .com registry), public registration record for hairbygerta.com. https://rdap.verisign.com/com/v1/domain/hairbygerta.com Confirms: a public record, not a help page. Read on 12 and on 13 October 2026: registrar Wix.com Ltd., registered 27 November 2025, expires 27 November 2026 at 01:04:09 UTC; also the lock status, the nameservers and the DNSSEC setting on those days. Read again on 2 November 2026: the same registration and expiry dates, client transfer prohibited and client update prohibited, nameservers NS2.WIXDNS.NET and NS3.WIXDNS.NET, DNSSEC on (delegationSigned true).
- [S28] ICANN, "ICANN Lookup" (registration data lookup tool). https://lookup.icann.org Confirms: a page where anyone can look up the current registration record of a domain name. The lookup was not run there for this guide; the record was read at the registry [S27].
- [S29] Wix Help Center, "Google Workspace: Checking Your Business Email Subscription Renewal Date". https://support.wix.com/en/article/google-workspace-checking-your-business-email-subscription-renewal-date Confirms: the Upcoming payment column for the business email; the Info icon; the date can differ from the expiration date when auto renew is off.
- [S30] Wix Help Center, "Google Workspace: Canceling Your Business Email Renewal". https://support.wix.com/en/article/google-workspace-canceling-your-business-email-renewal Confirms: renewal payments are attempted up to 30 days before the expiration date; a canceled business email works until the end of the paid period; the steps More Actions, Cancel subscription and what follows; Turn auto renew on; business emails bought through Wix are not refunded. The page has no steps for exporting mail.
- [S31] Wix Help Center, "Google Workspace: Availability of Business Email Data Following Cancellation". https://support.wix.com/en/article/google-workspace-availability-of-business-email-data-following-cancellation Confirms: after the paid period ends you can no longer read, receive or send email from the business mailbox; the data is kept under Google's retention rules and restored only if the business email is repurchased within that period; no number of days is given. The same article also opens under an older address that ends in availability-of-google-workspace-formerly-g-suite-mailbox-data-following-cancelation; the page has no steps for exporting mail.
- [S32] Google Account Help, "How to download your Google data". https://support.google.com/accounts/answer/3024190 Confirms: Google Takeout (takeout.google.com) exports and downloads your data, email included; its steps and option names; the waiting time; the 7 day expiry and the 5 download limit; changes made after the request may not be in the file.
- [S33] Wix Help Center, "Google Workspace: Accessing your Business Email Through Your Wix Account". https://support.wix.com/en/article/google-workspace-accessing-your-business-email-through-your-wix-account Confirms: sign in at Gmail.com with the full business address; switch Google account with the profile image or initial at the top right; the page has no steps for exporting mail.
- [S34] Google Workspace Admin Help, "Allow or block Google Takeout". https://knowledge.workspace.google.com/admin/users/advanced/allow-or-block-google-takeout Confirms: Takeout is allowed by default for Google Workspace and an administrator can change that (Admin console: Menu, Data, Data import & export, Google Takeout).
- [S35] Wix Help Center, "Transferring Your Wix Domain Away from Wix". https://support.wix.com/en/article/transferring-your-wix-domain-away-from-wix-2477749 Confirms: the transfer steps and button names; the code goes to the registrant contact email; usually up to 7 days; the Wix site is disconnected and MX records must be added again; who may transfer; privacy advice; the Whois Lookup status; the Grace Period.
- [S38] Wix Help Center, "ICANN's 60 Day Lock Policy". https://support.wix.com/en/article/icanns-60-day-lock-policy Confirms: Wix applies 60 days after registration, a contact change or a transfer; a locked domain can stay at Wix and be pointed to an external site; the advice to transfer before changing contact information.
- [S39] Wix Help Center, "Connecting a Wix Domain to an External Site". https://support.wix.com/en/article/connecting-a-wix-domain-to-an-external-site Confirms: Manage DNS Records; a Wix domain can point to an outside site by its A and CNAME records; nameservers cannot be changed.
- [S41] ICANN, "Transfer Policy" (updated 21 February 2024). https://www.icann.org/en/contracted-parties/accredited-registrars/resources/domain-name-transfers/policy Confirms: the 60-day periods; the five calendar days for the old registrar to answer; the five calendar days to give the code and remove the lock.
- [S42] ICANN, "FAQs for Registrants: Transferring Your Domain Name". https://www.icann.org/resources/pages/name-holder-faqs-2017-10-10-en Confirms: the same 60-day rules in plain words; the code within five calendar days; the registrar can be found with ICANN's lookup tool.
- [S45] Wix Help Center, "Wix Domains: Canceling Your Domain". https://support.wix.com/en/article/canceling-a-wix-domain Confirms: the steps to cancel auto renew; you keep the domain until the end of the period; no refunds for domains.
- [S53] Wix Help Center, "Activating DNSSEC for a Wix Domain". https://support.wix.com/en/article/activating-dnssec-for-a-wix-domain Confirms: the steps to turn off Privacy and DNSSEC protection; DNSSEC is only sold together with private registration; with the protection off, name and contact information can be seen in the WHOIS database; Turn On Protection switches it back on.
- [S54] Wix Help Center, "Viewing and Updating Your Wix Domain Contact Information". https://support.wix.com/en/article/viewing-and-updating-your-wix-domain-contact-information Confirms: changing the contact information locks the domain for 60 days; a new email address has to be confirmed from both the old and the new address; Wix recommends a registrant contact email that is not tied to the domain.
- [S55] ICANN, "2013 Registrar Accreditation Agreement", Whois Accuracy Program Specification. https://www.icann.org/en/contracted-parties/accredited-registrars/registrar-accreditation-agreement/2013-registrar-accreditation-agreement-17-09-2013-en Confirms: within 15 days of a transfer the registrar verifies the email address or the telephone number of the domain owner; without an answer it verifies by hand or suspends the registration.
- [S57] Wix Help Center, "Connecting a Domain to Wix Using the Pointing Method". https://support.wix.com/en/article/connecting-a-domain-to-wix-using-the-pointing-method Confirms: the Wix site must be upgraded before a domain can be connected; the steps and button names, among them the note on Start Transfer and the outline with I logged in, I found my domain settings, I found the records and I updated my records; the A and CNAME values, which are also shown on the Wix domains page; replace the records; it may take up to 48 hours; no DNSSEC and no DNS proxy.
- [S58] Wix Help Center, "Connecting a Domain You Own to Your Wix Site". https://support.wix.com/en/article/connecting-a-domain-you-own-to-your-wix-site Confirms: connecting is not transferring; the domain stays with its outside registrar.
- [S59] Wix Help Center, "Turning the Auto Renewal Off for a Wix Premium Subscription". https://support.wix.com/en/article/turning-the-auto-renewal-off-for-a-wix-premium-subscription Confirms: Wix subscriptions renew automatically unless auto renew is turned off; auto renew can be turned back on before the end of the subscription period; for a business email it names other last clicks than the page on canceling a business email.
- [S62] GitHub Docs, "Securing your GitHub Pages site with HTTPS". https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https Confirms: the Enforce HTTPS steps and that it redirects visitors to HTTPS; the automatic DNS check, the Let's Encrypt certificate and the check mark; Remove and Save again restarts the process; extra A, AAAA or CNAME records, or records not pointing to GitHub, can stop the certificate. Also confirms (checked on 2 November 2026): ALIAS and ANAME next to A and AAAA among the extra records on @ that can stop the certificate.
- [S63] GitHub Docs, "About repositories". https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories Confirms: a repository holds your files and each file's revision history.
- [S64] GitHub Docs, "Managing a custom domain for your GitHub Pages site". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site Confirms: the four A record addresses; the www CNAME points to the user name followed by .github.io without the repository name; Settings, Pages, "Custom domain", Save and Remove; add the domain in GitHub before changing DNS, and the warning about what can happen otherwise; the tip to verify the domain first; the CNAME file that GitHub adds and the need to pull it; the bare domain redirects to www; DNS changes can take up to 24 hours; Enforce HTTPS can take up to 24 hours to become available; people with admin permissions for the repository can set the custom domain; the dropdown menu (a three-dot icon) that holds Settings when the tab is not shown. Also confirms (checked on 2 November 2026): the four AAAA addresses 2606:50c0:8000::153 to 2606:50c0:8003::153; remove a default record that the DNS provider set; GitHub strongly recommends not using wildcard records such as *.example.com.
- [S65] GitHub Docs, "Troubleshooting custom domains and GitHub Pages". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/troubleshooting-custom-domains-and-github-pages Confirms: up to an hour until HTTPS works; removing and adding the domain again after DNS changes; the CNAME file must stay in the repository; the CAA rule; clearing the browser cache; what to do when the domain is already taken.
- [S66] GitHub Docs, "Verifying your custom domain for GitHub Pages". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages Confirms: what verifying protects against, the steps and button names, the wait of up to 24 hours, and that the TXT record must be kept; once a domain is verified, only repositories owned by the account that verified it may publish a GitHub Pages site to the domain or its immediate subdomains; the page does not describe how to remove a verification; verifying frees a domain that another GitHub user has taken. Also confirms (checked on 2 November 2026): the TXT record name has the form _github-pages-challenge-USERNAME.example.com.
- [S70] GitHub Docs, "About custom domains and GitHub Pages". https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/about-custom-domains-and-github-pages Confirms: GitHub Pages supports custom domains.
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
- [S101] Wix Help Center, "Domain Life Cycle". https://support.wix.com/en/article/domain-life-cycle Confirms: the Grace Period (about 30 days, no extra fee, domain no longer connected to the site, Extend Registration, private auction possible in the last 10 days); the Redemption Period (about 30 days, fee varies and is shown on the Domains page, Keep Domain, not guaranteed, up to 7 days); Pending Delete, then open to anyone after 5 to 10 days.
- [S102] ICANN, "5 Things every Domain Name Registrant should know about ICANN's Expired Registration Recovery Policy (ERRP)". https://www.icann.org/resources/pages/registrant-about-errp-2018-12-07-en Confirms: the website and email of an expired name are interrupted before it is deleted and during redemption; a Redemption Grace Period of 30 days in which the name can be restored; the registrar may charge a fee.
- [S103] Wix Help Center, "Wix Domain Renewal Payment Failure". https://support.wix.com/en/article/wix-domain-renewal-payment-failure Confirms: the 30 day grace period at no extra fee; a redemption fee of \$100; if the payment attempt fails, the domain expires on the anniversary of the original payment.
- [S104] Wix Help Center, "Transferring an Expired Wix Domain to Another Domain Host". https://support.wix.com/en/article/transferring-an-expired-wix-domain-to-another-domain-host Confirms: an expired domain can be transferred only during the grace period, not in the redemption period; a \$100 retrieval fee; when extending a domain, changing its contact info locks it from transfer for 60 days.
- [S105] Wix Help Center, "Extending Your Wix Domain Subscription". https://support.wix.com/en/article/extending-your-wix-domain-subscription Confirms: the steps Domains, Extend, registration period, Continue, privacy option, Continue, payment information, Submit Purchase.
- [S106] Google Workspace Help, "Cancel Google Workspace" (last updated 9 October 2026). https://knowledge.workspace.google.com/admin/billing/cancel-google-workspace Confirms: after a subscription bought from Google is canceled, user data is deleted and cannot be restored; customers of a reseller are sent to a different page.
- [S107] Wix Help Center, "Closing Your Wix Account". https://support.wix.com/en/article/closing-your-wix-account Confirms: closing the account cannot be undone and you lose access to everything in it; you do not need to wait for a canceled subscription to expire; a canceled domain stays registered until it expires; the account can stay open for free after the premium subscriptions are canceled.
- [S108] GitHub Docs, "GitHub Pages limits". https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits Confirms: GitHub Pages is available in public repositories with GitHub Free; the 1 GB site limit and the 100 GB soft bandwidth limit; the rule against using Pages as free hosting for an online business or shop.
- [S113] Wix Help Center, "Downloading Invoices for Wix Subscriptions and Services". https://support.wix.com/en/article/downloading-invoices-for-wix-subscriptions Confirms: the address of the Billing History page; the More Actions icon; View Invoice.
- [S114] Wix Help Center, "Managing Invoices Paid for Wix Services". https://support.wix.com/en/article/managing-invoices-paid-for-wix-services Confirms: the Billing History page holds all invoices for services paid at Wix; the All Dates drop-down; services with the same renewal date may share one invoice.
- [S115] GitHub Docs, "Creating a new repository". https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository Confirms: the plus icon labeled "Create something new", New repository, the Owner dropdown menu, the "Repository name" field, choosing a visibility, the optional README, .gitignore and license, Create repository.
- [S116] GitHub Docs, "Adding locally hosted code to GitHub". https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github Confirms: do not initialize the new repository with README, license or gitignore files, to avoid errors; copy the repository address from the Quick Setup page; Git Bash on Windows; the commands git init -b main, git add ., git commit -m "First commit", git remote add origin REMOTE-URL and git push -u origin main.
- [S120] Porkbun Knowledge Base, "How to Transfer a Domain to Porkbun". https://kb.porkbun.com/article/56-how-to-transfer-a-domain-to-porkbun Confirms: unlock the domain and get the authorization (EPP) code at the old registrar, the code works once; start at porkbun.com/transfer or the TRANSFER link at the top; type the domain without www in **Domain Name**, the code in **Auth Code**, click **Submit**, leave the first two boxes ticked (WHOIS privacy and auto renew), choose a DNS option, click **Add Transfers to Cart**, then **Continue to Billing**; a transfer takes 5 to 7 business days; status under **Transfer** in the top menu; a transfer can be refused within 60 days of registration, when the domain has expired or is about to, or with more than 9 years left; in most cases no time is lost and a year is added.
- [S121] Porkbun, "Domain Transfer" page. https://porkbun.com/transfer Confirms: the fields **Domain Name** and **Auth Code**, the buttons **Submit** and **Add Transfers to Cart**; the boxes "Automatically turn on WHOIS privacy / data redaction after domains transfer in." and "Automatically enable auto renewal so your domains don't accidentally expire after they transfer in."; the two DNS choices "Pause my transfer until I've set up DNS here." and "Move DNS to Porkbun after the transfer, without pausing anything." (the second copies the records Porkbun can find now and puts the domain on Porkbun DNS when the transfer is done, and Porkbun says its lookup cannot see every record, so check them afterwards); gTLD transfers include a one year renewal unless the domain is inside the auto renew grace period.
- [S122] Porkbun Knowledge Base, "What Do Transfer Statuses Mean?". https://kb.porkbun.com/article/79-what-do-transfer-statuses-mean Confirms: the **Transfer** button at the top opens the **Domain Transfers** page; the statuses pending transfer from losing registrar (5 to 7 days), pending owner confirmation (an email goes to the registrant contact, follow its link), bad authcode (**Update authcode** under **Options**), domain status does not allow transfer (unlock it at the old registrar) and transfer complete (the domain shows in **Domain Management** within minutes).
- [S123] Porkbun Knowledge Base, "How Long Will It Take to Transfer My Domain to Porkbun?". https://kb.porkbun.com/article/36-how-long-will-it-take-to-transfer-my-domain-to-porkbun Confirms: usually five to seven days; Porkbun sends an email when it is finished.
- [S124] Porkbun Knowledge Base, "Will I Lose Domain Registration Time if I Transfer?". https://kb.porkbun.com/article/55-lose-domain-registration-time-if-transfer-domains Confirms: no registration time is lost and in most cases a year is added; the year is not added when the transfer happens fewer than 45 days after the day the domain expired or fewer than five days after it was renewed.
- [S125] Porkbun Knowledge Base, "How to Transfer a Domain to Porkbun With No Downtime". https://kb.porkbun.com/article/89-how-to-transfer-a-domain-to-porkbun-with-no-downtime Confirms: if a domain has DNSSEC records, Porkbun recommends deleting them before the transfer to prevent DNS problems; DNSSEC can be turned on again at Porkbun afterwards.
- [S126] Porkbun Knowledge Base, "Will My Nameservers Be Imported During a Transfer?". https://kb.porkbun.com/article/117-will-my-nameservers-be-imported-during-a-transfer Confirms: Porkbun does not change the nameservers of a domain when it transfers in; a domain that used the old registrar's nameservers has to be switched to Porkbun's nameservers and its records made again.
- [S127] Porkbun Knowledge Base, "How to Switch to Porkbun's Nameservers". https://kb.porkbun.com/article/63-how-to-switch-to-porkbuns-nameservers Confirms: **ACCOUNT**, **Domain Management**, **Details** next to the domain, the edit icon next to the nameservers, **Use Our Default Nameservers**, **Save Nameservers**; the default nameservers are curitiba.ns.porkbun.com, fortaleza.ns.porkbun.com, maceio.ns.porkbun.com and salvador.ns.porkbun.com; a change can take up to 48 hours, most finish within a few hours.
- [S128] Porkbun Knowledge Base, "How to Change Nameservers". https://kb.porkbun.com/article/22-how-to-change-nameservers Confirms: the same path, **Save Nameservers**, and **Submit** if asked; up to 48 hours.
- [S129] Porkbun Knowledge Base, "How to Edit DNS Records". https://kb.porkbun.com/article/68-how-to-edit-dns-records Confirms: **Details**, the edit icon next to **DNS Records**, the **Manage DNS Records** page, **Add Record**, **Add**, **Back**; the pencil icon edits a record and the trash can icon deletes it after **OK**.
- [S130] Porkbun Knowledge Base, "How to Add DNS Records on Porkbun". https://kb.porkbun.com/article/231-how-to-add-dns-records-on-porkbun Confirms: the fields **Type**, **Host** (empty for the domain itself), **Answer** (for an A record the IPv4 address), **TTL** (keep the default), **Notes** (optional) and **Priority** (MX records); the button **Add**; a CNAME needs a host and a full domain name as the answer; an AAAA answer is an IPv6 address; TXT records are mostly used to prove ownership. Also confirms: the Type option "A - Address record"; the label of the Answer field changes with the record type, for an A record it is "IPv4 Address".
- [S131] Porkbun Knowledge Base, "CNAME, ALIAS Record With That Host Already Exists Error". https://kb.porkbun.com/article/239-cname-alias-record-with-that-host-already-exists-error Confirms: Porkbun's default records point to pixie.porkbun.com and show its parking page; delete them, and delete records left from a previous host, before adding your own.
- [S132] Porkbun Knowledge Base, "How to Set Up Email Forwarding Service". https://kb.porkbun.com/article/10-how-to-set-up-email-forwarding-service Confirms: **Domain Management**, the envelope icon in the **EMAIL** column, the **Email Hosting and Forwarding** page, the **Porkbun Email Forwarding** section, **Create a New Forwarding Address** (user name and destination), **Create Email Forward**, the **Current Forwards** list; up to 20 free forwards per domain; no wildcard or catch-all; replies go out from the personal address; one forward can go to more than one address; test from a different address than the destination; the MX records must point to Porkbun.
- [S133] Porkbun Knowledge Base, "How to Reset DNS and Park Your Domain". https://kb.porkbun.com/article/183-how-to-reset-dns-and-park-your-domain Confirms: the email forwarding records are MX (host empty) fwd1.porkbun.com priority 10, MX (host empty) fwd2.porkbun.com priority 20 and TXT (host empty) v=spf1 include:_spf.porkbun.com ~all; a **Fix DNS** button at the bottom of the **Email Hosting and Forwarding** page adds them.
- [S134] Porkbun Knowledge Base, "How to Use Porkbun Email When Your DNS Is Hosted Elsewhere". https://kb.porkbun.com/article/47-how-to-use-porkbun-email-when-your-dns-is-hosted-elsewhere Confirms: the same MX and SPF records; delete other MX records for the domain itself; a domain may have only one SPF record, so two have to be merged into one.
- [S135] Porkbun Knowledge Base, "Hosted Email vs. Email Forwarding". https://kb.porkbun.com/article/67-hosted-email-vs-email-forwarding Confirms: hosted email costs \$3 a month per address, billed yearly; forwarding only receives mail and passes it on.
- [S136] Porkbun Knowledge Base, "How to Configure WHOIS Privacy Service". https://kb.porkbun.com/article/97-how-to-configure-whois-privacy-service-porkbun Confirms: WHOIS privacy is free; it is on by default for new registrations; the eye icon under **WHOIS** offers **Redact Privacy Data**, **Use Privacy Service** and **Make Public**.
- [S137] Porkbun, "Free WHOIS Privacy". https://porkbun.com/products/whois_privacy Confirms: free WHOIS privacy for all participating domains registered with or transferred to Porkbun.
- [S138] Porkbun Knowledge Base, "How to Turn Off Auto Renew". https://kb.porkbun.com/article/70-how-to-turn-off-auto-renew Confirms: the icon in the **Renew** column, **Disable Auto Renew** and **Enable Auto Renew**.
- [S139] Porkbun Knowledge Base, "How to Check a Domain's Renewal Price". https://kb.porkbun.com/article/108-how-to-check-domain-renewal-price Confirms: **Details** next to the domain shows the **Renewal Price**.
- [S140] Porkbun Knowledge Base, "Why Did .com Prices Go Up and How High Will They Go?" (updated 27 May 2026). https://kb.porkbun.com/article/201-why-did-com-prices-go-up-and-how-high-will-they-go Confirms: the .com price rises on 1 November 2026 at 04:00 UTC to about \$11.81, and is expected to rise about 7% a year from 2026 to 2030.
- [S141] Porkbun, "Domain Name Pricing". https://porkbun.com/products/domains Confirms: .com registration, renewal and transfer each \$11.81, all fees included; most transfers include a one year renewal.
- [S142] Porkbun Knowledge Base, "How to Enable DNSSEC". https://kb.porkbun.com/article/216 Confirms: the **Porkbun DNSSEC** switch under **Details**.
- [S143] Google Search Console Help, "Sitemaps report". https://support.google.com/webmasters/answer/7451001 Confirms: an owner of the property adds a sitemap under **Add a new sitemap** with its full address and **Submit**; the status shows Success, Has errors or Couldn't fetch. Also confirms: test first that the sitemap is available to Google; the Sitemap URL is the exact address submitted and redirects are not followed; do not confuse www and non-www properties; click a row that is not Success to see the errors; resubmit after big changes.
- [S150] Porkbun Knowledge Base, "How to Change Domain and Account Contact Information". https://kb.porkbun.com/article/57-how-to-change-contact-information Confirms: **ACCOUNT**, **Settings / Billing**, the section **Registration Defaults**, the header **Default Contacts**, the pencil icon next to **REGISTRANT**; new domains are filled in with the data of the default contacts; one domain's contacts are changed under **Details**, **Contacts**, the **DOMAIN CONTACTS** pop-up, **Submit**. The page does not say whether the defaults are used for transferred domains.
- [S151] IETF, RFC 9083 "JSON Responses for the Registration Data Access Protocol (RDAP)", section 5.3. https://www.rfc-editor.org/rfc/rfc9083.html Confirms: in a public record (RDAP), the member secureDNS has delegationSigned, which is true if there are DS records in the parent zone and false otherwise, and dsData, the list of those DS records.
- [S152] ICANN, "EPP Status Codes: What Do They Mean, and Why Should I Know?". https://www.icann.org/resources/pages/epp-status-codes-2014-06-16-en Confirms: the status clientTransferProhibited tells the registry to reject requests to transfer the domain; to transfer the domain you first ask the registrar to remove it; a domain's status codes show in a Whois lookup.
- [S154] Wix Help Center, "Price of Wix Domain Renewals". https://support.wix.com/en/article/price-of-wix-domain-renewals-6790543 Confirms: the cost of a Wix domain depends on the domain extension, the local currency, the number of years, optional privacy protection and local tax or VAT; the renewal cost shows under **Premium Subscriptions**, **View payment details** in the **Upcoming payment** column. The page gives no price.
- [S155] Google Search Console Help, "Verify your site ownership". https://support.google.com/webmasters/answer/9008080 Confirms: Search Console periodically checks that the verification token is still present and valid; to stay verified, do not remove the DNS record from the provider, even after verification succeeds; if verification can no longer be confirmed, permissions on the property expire after a grace period.
- [S156] Wix Help Center, "Adding or Updating TXT Records in Your Wix Account". https://support.wix.com/en/article/adding-or-updating-txt-records-in-your-wix-account Confirms: Domains, the Domain Actions icon, Manage DNS Records, + Add Record in the TXT (Text) section, the Host Name field (left blank for @), the Value field, Save; for a domain connected by pointing, TXT records are added at the domain host. The page does not say how long a change takes and does not show what stands next to the Host Name field.
- [S160] Wix Help Center, "Google Workspace: FAQs". https://support.wix.com/en/article/google-workspace-faqs Confirms: a Google Workspace business email can be transferred from a Wix account to Google by contacting Wix Customer Care; this is an irreversible action; it disconnects the business email from the Wix account, and the business email cannot then be bought again through Wix.
- [S161] Google Workspace Admin Help, "Set up MX records for Google Workspace" (last updated 26 October 2026). https://knowledge.workspace.google.com/admin/domains/set-up-mx-records-for-google-workspace Confirms: the Google Workspace MX record value is smtp.google.com with priority 1; older MX values that start with aspmx are still supported; MX record changes take some time to be recognized across the internet.
- [S162] Google Workspace Admin Help, "Avoid issues when changing MX records" (last updated 26 October 2026). https://knowledge.workspace.google.com/admin/domains/avoid-issues-when-changing-mx-records Confirms: until the new MX records are active, emails are directed to the previous email provider.
- [S165] Porkbun, "Free DNS Management". https://porkbun.com/products/dns_management Confirms: Porkbun offers DNS management for your domain for free; the page ties it to registering a domain and does not mention transfers or give a price.
- [S166] Porkbun Knowledge Base, "How to Renew Domain Names". https://kb.porkbun.com/article/45-how-to-renew-domain-name Confirms: a domain renews automatically as its expiration date approaches if a credit card is on file and auto renew is turned on for it; manual renewal by the icon in the **Renew** column, the **Manual Renewals** section with the **Domain** box, **Add Renewals to Cart** and **Continue to Billing**; total registration time may never exceed ten years. The page does not say how many days before expiry the renewal happens or what happens when a payment fails.
- [S167] Porkbun Knowledge Base, "How to update your credit card billing information". https://kb.porkbun.com/article/142-how-to-update-your-credit-card-billing-information Confirms: **ACCOUNT**, **Settings / Billing**, the **Billing Information** section, **Update Card**, **Submit**; the card shows on the Settings / Billing page.
- [S168] Porkbun, "Domain Name Registration Agreement" (effective 17 March 2025). https://porkbun.com/legal/agreement/domain_name_registration_agreement Confirms: in "Term of Service", unless automatic renewal is disabled Porkbun attempts to renew the services as they come up for renewal, takes payment from the payment method on the account (or account credit), charges its then-current rates, which may be higher or lower, and renewal payments are final and non-refundable; if an automatic renewal cannot be processed and the problem is not fixed, the services expire; in "Domain Renewal Notification Policy", notices go to the registered name holder's primary email address about 1 month and 1 week before expiration, and one more 5 days after expiration. The agreement gives no number of days for when the renewal is charged.
