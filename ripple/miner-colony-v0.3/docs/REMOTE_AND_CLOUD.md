# Authorized remote workers and cloud: actual connection procedure

The remote worker is a real computational endpoint, not a cloud-account simulator. It can run on a Linux host you own or rent **only if the provider permits mining**. The current release never provisions compute, authorizes payment, configures a mining account, or incurs charges by itself.

### Local end-to-end test (same computer)

On terminal A, generate a private random token (at least 20 characters) and export it as `RIPPLE_REMOTE_TOKEN`; for example, use `python -c "import secrets; print(secrets.token_urlsafe(32))"`. Run:

```sh
export RIPPLE_REMOTE_TOKEN='YOUR_GENERATED_TOKEN_HERE'
python -m ripple_miner.remote --host 127.0.0.1 --port 8898
```

From the dashboard, enter `http://127.0.0.1:8898`, its token, and your actual Stratum pool details. Set worker count at least 1. The miner launches a local worker plus a separately addressed remote logical worker. To verify WITHOUT an external pool or payouts, run `python -m unittest discover -s tests -v`.

### Remote cloud-owned CPU

Run the same service on your authorized Linux VM. For public network connections, start with an operator-provided TLS certificate and private key:

```sh
export RIPPLE_REMOTE_TOKEN='YOUR_GENERATED_TOKEN_HERE'
python -m ripple_miner.remote --host 0.0.0.0 --port 8898 --tls-cert /secure/cert.pem --tls-key /secure/key.pem
```

Restrict the firewall to the controller's IP and use a DNS hostname matching a trusted TLS certificate. In the dashboard, enter `https://your-authorized-worker.example:8898` and the token. When an hourly price is known from your actual contract, enter it to estimate remote-worker processing cost from measured dispatch wall time. This is **not** a provider invoice or payout.

### Android monitoring

By default the service listens to `127.0.0.1:8877`, so an Android phone on the LAN cannot automatically reach it. If USB debugging and an Android SDK `adb` installation are available, connect the phone and run on the Dell:

```sh
adb reverse tcp:8877 tcp:8877
```

Then open `http://127.0.0.1:8877` in the phone's browser and authenticate with the Dell-generated local token. This exposes the PC loopback service only through an operator-authorized USB debugging session. For wireless use, deploy an authenticated and encrypted private access tunnel separately; do not expose port 8877 directly to the public internet.

### Policy

Google Cloud's free trial excludes cryptomining; its paid services require prior written mining approval. Provider policy must be checked for the chosen product/region. Stratum V1 can submit real pool shares, but CPU profitability is almost certainly uneconomic at Bitcoin network difficulty.
