variable "yc_service_account_key_file" {
  type        = string
  description = "Путь к файлу с авторизованным ключом сервисного аккаунта"
}

variable "yc_cloud_id" {
  type        = string
  description = "Идентификатор вашего облака в Yandex Cloud"
}

variable "yc_folder_id" {
  type        = string
  description = "Идентификатор каталога внутри облака"
}

variable "yc_zone" {
  type        = string
  default     = "ru-central1-a"
  description = "Географическая зона доступности"
}