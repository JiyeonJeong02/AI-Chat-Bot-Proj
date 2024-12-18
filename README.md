# 5조

🚧🚧 우리 FIS 아카데미 최종 프로젝트 🚧🚧

## 멤버

<table>
 <tr>
    <td align="center"><a href="https://github.com/awesome98"><img src="https://avatars.githubusercontent.com/awesome98" width="150px;" alt=""></td>
    <td align="center"><a href="https://github.com/eunchaipark"><img src="https://avatars.githubusercontent.com/eunchaipark" width="150px;" alt=""></td>
    <td align="center"><a href="https://github.com/euneun9"><img src="https://avatars.githubusercontent.com/euneun9" width="150px;" alt=""></td>
    <td align="center"><a href="https://github.com/JiyeonJeong02"><img src="https://avatars.githubusercontent.com/JiyeonJeong02" width="150px;" alt=""></td>
    <td align="center"><a href="https://github.com/yonggaljjw"><img src="https://avatars.githubusercontent.com/yonggaljjw" width="150px;" alt=""></td>
    <td align="center"><a href="https://github.com/SukbeomH"><img src="https://avatars.githubusercontent.com/SukbeomH" width="150px;" alt=""></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/awesome98"><b>👑 신호섭</b></td>
    <td align="center"><a href="https://github.com/eunchaipark"><b>박은채</b></td>
    <td align="center"><a href="https://github.com/euneun9"><b>이은지</b></td>
    <td align="center"><a href="https://github.com/JiyeonJeong02"><b>정지연</b></td>
    <td align="center"><a href="https://github.com/yonggaljjw"><b>조진원</b></td>
    <td align="center"><a href="https://github.com/SukbeomH"><b>홍석범</b></td>
  </tr>
</table>

## Manuals

### Git

- [git convention](./Documents/Manual/gitConvention.md)
- [git](./Documents/Manual/git.md)

## Project Structure

![project structure](./Documents/diagrams/systemArchitecture.drawio.png)

> [draw.io](https://app.diagrams.net/)를 이용하여 작성하였습니다.

- **Airflow**: 주기적으로 데이터를 수집하고, 전처리하는 역할을 합니다.
- **Elasticsearch**: 수집된 데이터를 저장하고, 백터화된 데이터를 저장, 검색하는 역할을 합니다.
- **Kibana**: Elasticsearch에 저장된 데이터를 시각화하는 역할을 합니다.
- **Django**: 사용자에게 데이터를 제공하고, 사용자의 요청에 따라 데이터를 Elasticsearch에서 가져와서 제공하는 역할을 합니다.
- **MySQL**: 사용자의 정보를 저장하고, Django에서 사용하는 데이터를 저장하는 역할을 합니다.

## Tech Stack

- Python 3.11
- Django 5.0
- MySQL 8.0
- Elasticsearch 7.15
