# Buttondown Setup (one-time, ~15 min)

The footer subscribe form is wired but currently posts to `YOUR_BUTTONDOWN_USERNAME` placeholder. After Buttondown signup, replace it.

## 1. Sign up

- Go to https://buttondown.email/register
- Pick the **Hobby** plan if under 100 subscribers, or **Standard** ($9/mo) for up to 1000. Both have RSS-to-email.
- Choose a username (will be your form endpoint). Suggested: `singaporerabbit` or `sg-rabbits`.

## 2. Replace the placeholder in the footer

```
git grep YOUR_BUTTONDOWN_USERNAME
# src/components/Footer.astro:3 occurrences
```

Edit `src/components/Footer.astro` and replace `YOUR_BUTTONDOWN_USERNAME` with your actual username (both the form action URL and the popup URL).

## 3. Set up RSS-to-email automation

In the Buttondown dashboard:

1. Settings → Automation → RSS-to-email
2. Add feed URL: `https://singaporerabbit.com/rss.xml`
3. Schedule: weekly digest, every **Monday 9am SGT**
4. Subject line template: `weekly rabbit digest — {{title}}` (Buttondown substitutes the latest post title)
5. Test send to your own email first
6. Enable

This will:
- Pull new entries from your RSS feed every Monday morning
- Bundle them into one email
- Send to all subscribers
- No further action required from you

## 4. Verify the form works

After deploy:
- Open https://singaporerabbit.com/ in incognito
- Submit a test email at the footer form
- Confirm you see the Buttondown welcome page popup
- Check Buttondown dashboard → Subscribers → new test email appears

## 5. Optional: customize the welcome email

Buttondown → Settings → Welcome email. Write something short:

```
hi —

thanks for subscribing to the singaporerabbit digest.
one short email each Monday with new guides, vet updates,
and SG-specific seasonal reminders.

if you ever want to add a vet, shop, or rescue to our directory,
just reply to this email. we read every one.

— xavier + the singaporerabbit team
```

## 6. Once subscriber count is healthy (50+)

Consider:
- Run a one-off **announcement** email when shipping a major guide (e.g., the GI stasis or first-week ones)
- Survey subscribers (Buttondown supports embedded surveys) on what topics they want
- Add subscriber count to the about page once it crosses 500 (social proof)
