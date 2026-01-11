# Sources and terms

Researched during the build; source dates and the historical data period are distinct from simulated local commit timestamps.

| Claim or decision | Primary evidence |
|---|---|
| Manual review adds expertise, but can delay good customers; prioritize where it adds value | [Stripe review documentation](https://docs.stripe.com/radar/transaction-reviews), particularly Best practices |
| Review policy changes should be tested against historical outcomes | [Stripe rule testing](https://docs.stripe.com/radar/testing) |
| ULB/Worldline dataset, 284,807 transactions, 492 frauds, September 2013, PCA features; accuracy is misleading | [Original dataset card](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) |
| Data license is separate from code license | Dataset card lists “Database: Open Database, Contents: Database Contents”; [ODbL](https://opendatacommons.org/licenses/odbl/1-0/) and [Database Contents License](https://opendatacommons.org/licenses/dbcl/1-0/). Raw data is not redistributed here. |
| Public-repository standard hosted CI is free | [GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) |
| Pages public-repository availability and free hosting constraints | [Pages overview](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages), [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) |
| Candidate chart components investigated | [shadcn chart docs](https://ui.shadcn.com/docs/components/base/chart) — composable Recharts; rejected extra framework dependency for this compact static UI |
| Motion and reduced-motion behavior investigated | [Motion accessibility guide](https://motion.dev/docs/react-accessibility) — kept native CSS transitions and an explicit reduced-motion rule instead of a runtime animation dependency |
| Modern build tooling | [Vite 8 release](https://vite.dev/blog/announcing-vite8) and [supported release lines](https://vite.dev/releases); exact installed version lives in package-lock.json |

Product design references: [Stripe Radar](https://stripe.com/radar), [Sift Console pictured in its product primer](https://sift.com/wp-content/uploads/2025/06/Primer_Sift-for-Streaming-Services-Fraud.pdf), and [Adyen Protect](https://docs.adyen.com/risk-management). These establish the relevant comparison space, not endorsements or proof of equivalent production capabilities. The design review documents which interface qualities are useful and which belong to a different operational scope.

The ULB dataset attribution remains Worldline and the Machine Learning Group at Université Libre de Bruxelles. Cite Dal Pozzolo et al., *Calibrating Probability with Undersampling for Unbalanced Classification*, IEEE CIDM (2015), as requested by the dataset card. The checked-in benchmark is a produced aggregate statistical work; its source is explicitly linked and users reproduce locally under the original database terms. Code license is the existing MIT license; that does not relicense the source data.
