# DNS records for lengkundee.org

data "aws_route53_zone" "lengkundee_org" {
  name         = "lengkundee.org."
  private_zone = false
}

resource "aws_route53_record" "github_pages_verification" {
  zone_id = data.aws_route53_zone.lengkundee_org.zone_id
  name    = "_github-pages-challenge-Mouy-leng.lengkundee.org"
  type    = "TXT"
  ttl     = 3600
  records = ["\"3a64cd63e42a9263bd186598d42dc7\""]
}
