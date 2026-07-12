export const MOCK_RESPONSE = {
  probability: 0.73,
  shap_values: {
    cpu_rolling_mean: 0.31,
    ram_rolling_std: 0.18,
    latency_lag_1: 0.12,
    disk_io_rate: -0.05,
    network_io_rolling_mean: 0.09,
    deploy_flag: 0.02,
  },
};

export const MOCK_POINTS = [
  { timestamp: "2024-01-15T10:00:00Z", cpu: 45, ram: 55, latency: 120, disk_io: 30, network_io: 40, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:00:15Z", cpu: 48, ram: 57, latency: 135, disk_io: 32, network_io: 42, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:00:30Z", cpu: 52, ram: 60, latency: 150, disk_io: 35, network_io: 45, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:00:45Z", cpu: 55, ram: 62, latency: 180, disk_io: 38, network_io: 48, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:01:00Z", cpu: 58, ram: 63, latency: 200, disk_io: 40, network_io: 50, deploy_flag: 1 },
  { timestamp: "2024-01-15T10:01:15Z", cpu: 62, ram: 65, latency: 250, disk_io: 42, network_io: 55, deploy_flag: 1 },
  { timestamp: "2024-01-15T10:01:30Z", cpu: 65, ram: 68, latency: 310, disk_io: 45, network_io: 58, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:01:45Z", cpu: 70, ram: 70, latency: 350, disk_io: 48, network_io: 60, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:02:00Z", cpu: 72, ram: 72, latency: 400, disk_io: 50, network_io: 62, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:02:15Z", cpu: 75, ram: 74, latency: 450, disk_io: 52, network_io: 65, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:02:30Z", cpu: 78, ram: 76, latency: 500, disk_io: 55, network_io: 68, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:02:45Z", cpu: 80, ram: 78, latency: 550, disk_io: 58, network_io: 70, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:03:00Z", cpu: 82, ram: 79, latency: 600, disk_io: 60, network_io: 72, deploy_flag: 1 },
  { timestamp: "2024-01-15T10:03:15Z", cpu: 85, ram: 80, latency: 650, disk_io: 62, network_io: 75, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:03:30Z", cpu: 83, ram: 82, latency: 700, disk_io: 65, network_io: 78, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:03:45Z", cpu: 87, ram: 83, latency: 750, disk_io: 68, network_io: 80, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:04:00Z", cpu: 88, ram: 84, latency: 780, disk_io: 70, network_io: 82, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:04:15Z", cpu: 86, ram: 85, latency: 800, disk_io: 72, network_io: 85, deploy_flag: 0 },
  { timestamp: "2024-01-15T10:04:30Z", cpu: 90, ram: 82, latency: 750, disk_io: 75, network_io: 88, deploy_flag: 1 },
  { timestamp: "2024-01-15T10:04:45Z", cpu: 85, ram: 80, latency: 680, disk_io: 70, network_io: 85, deploy_flag: 0 },
];
