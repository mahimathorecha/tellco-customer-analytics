# TellCo Customer Analytics

Project 5 dashboard for telecom customer usage, engagement, network experience, and a calculated satisfaction proxy.

## Run locally

Use Python 3.13 (the original dashboard was run with Python 3.13.7). From this folder:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Keep the terminal running and open the local URL it prints. No MySQL or MLflow server is required for these dashboard pages: they read the supplied CSV exports.

## Pages

- **app**: Satisfaction proxy, cluster comparisons, score relationships, customer lookup, and filtered CSV download.
- **Usage**: Sessions, traffic, application totals, and top customers.
- **Engagement**: Cluster profiles using session count, duration, and traffic.
- **Network Experience**: Throughput, RTT, retransmissions, handset comparisons, and distributions.

## Data

Each CSV contains 106,856 unique customer rows. The same customer has the same replacement ID in every file. Original customer identifiers have been replaced by randomly assigned labels such as `C000001`. The lookup mapping is not included. Other values and row order are preserved. This is pseudonymization, not a guarantee that all remaining data is anonymous.

| File | Contents |
| --- | --- |
| customer_scores.csv | Engagement, experience, satisfaction proxy, and satisfaction cluster |
| customer_usage.csv | Session duration, count, and application traffic |
| engagement.csv | Engagement features and cluster labels |
| customer_experience.csv | Network metrics, handset type, and experience cluster |

## Interpretation

- Satisfaction is the arithmetic mean of the engagement and experience scores, not a customer survey rating.
- The separate linear regression model predicts this constructed proxy from its components; a perfect fit does not validate real customer satisfaction.
- Cluster numbers are group identifiers, not quality rankings.
- Missing-value and outlier replacement can influence network comparisons.
- Application traffic totals are shown separately from overall download plus upload traffic and are not assumed to reconcile.
- Traffic uses decimal GB (1,000,000,000 bytes); durations use hours.

## Repository scope

This package contains the dashboard and prepared CSV exports. The analysis notebook, MySQL export code, MLflow model and monitoring evidence, final report, and presentation are separate project deliverables.

## Deployment entry point

If these files are uploaded at the repository root, the dashboard entry point is `app.py` and dependencies are in `requirements.txt`. Preserve the `pages` subfolder. Review dataset sharing permissions before making the repository or dashboard public.
