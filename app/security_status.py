from security_guard import assert_zero_egress, print_security_status

if __name__ == "__main__":
    print_security_status()
    assert_zero_egress("security_status", "manual_status_check")
