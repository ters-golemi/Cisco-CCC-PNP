# Lab Setup Checklist

## Pre-Lab Checklist (30 minutes before lab)

### Infrastructure Verification
- [ ] Catalyst Center accessible at https://172.16.1.10
- [ ] DHCP server responding with Option 43
- [ ] Network devices powered and accessible
- [ ] Student workstations have internet access
- [ ] Git repository accessible

### Quick Tests
```bash
# Test Catalyst Center connectivity
curl -k https://172.16.1.10/dna/system/api/v1/auth/token

# Test DHCP Option 43
nmap --script dhcp-discover 10.10.10.1

# Test Python environment
python3 -c "import requests, yaml, jinja2; print('OK')"
```

## During Lab Monitoring

### Student Progress Checkpoints
1. **15 min**: Environment setup complete
2. **45 min**: DHCP Option 43 configured
3. **90 min**: First device discovered
4. **120 min**: Configurations generated
5. **150 min**: Devices deployed
6. **180 min**: Verification complete

### Common Issues Watch List
- Python import errors (first 15 minutes)
- DHCP Option 43 misconfiguration (30-60 minutes)
- Authentication failures (60-90 minutes)
- Template syntax errors (90-120 minutes)

## Post-Lab Cleanup (15 minutes)

### Automated Cleanup
```bash
# Run cleanup script
./cleanup_lab_environment.sh

# Verify reset
python3 verify_lab_reset.py
```

### Manual Verification
- [ ] All devices factory reset
- [ ] Catalyst Center PnP inventory cleared
- [ ] Student directories reset
- [ ] DHCP leases cleared
- [ ] Network connectivity restored