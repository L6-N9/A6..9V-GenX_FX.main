# GenX FX Hardware Configuration

This document tracks the hardware configuration of the system running the GenX FX Trading Platform.

## 💾 Storage Devices

Last Updated: 2026-01-25

### Disk 1 (F:)
- **Device**: SSK SSK USB Device
- **Capacity**: 477 GB
- **Type**: USB
- **Usage**: Primary Backup / Extended Storage
- **Status**: Active

### Disk 2 (E:)
- **Device**: TOSHIBA MQ01ACF050 SCSI Disk Device
- **Capacity**: 466 GB
- **Type**: USB (SCSI Disk)
- **Usage**: Secondary Backup
- **Status**: Active

### Disk 0 (C:)
- **Usage**: System Drive (OS & Applications)

### Disk (D:)
- **Usage**: Main Project Drive (GenX FX Project Files)
- **Status**: Active

---

## 🔧 Drive Management

The system is configured to use **D:** drive as the primary location for the GenX FX platform to ensure high performance.
**E:** and **F:** drives are utilized for automated backups and redundant data storage.

### Backup Strategy
1. **Daily Backup**: Automatically synced to Disk 2 (E:).
2. **Weekly Full Backup**: Manually or automatically synced to Disk 1 (F:).
3. **Offsite/Cloud**: Important credentials and configs are additionally backed up to cloud services.
