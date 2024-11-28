document.addEventListener("DOMContentLoaded", function () {
	// 이벤트 위임을 사용한 토글 버튼 처리
	document
		.querySelector(".toggle-container")
		.addEventListener("click", function (e) {
			if (e.target.classList.contains("toggle-button")) {
				const chartId = e.target.dataset.chart;

				// 버튼 스타일 업데이트
				document.querySelectorAll(".toggle-button").forEach((btn) => {
					btn.classList.remove("active");
					btn.classList.add("inactive");
				});
				e.target.classList.remove("inactive");
				e.target.classList.add("active");

				// 차트 표시 로직을 requestAnimationFrame으로 래핑
				requestAnimationFrame(() => {
					showChart(chartId);
				});
			}
		});

	// 사이드바 버튼 이벤트 리스너 추가
	const sidebarButtons = document.querySelectorAll("[data-page]");
	sidebarButtons.forEach((button) => {
		button.addEventListener("click", function () {
			const pageId = this.dataset.page;

			// 모든 사이드바 버튼의 스타일 초기화
			sidebarButtons.forEach((btn) => {
				btn.classList.remove("bg-gray-300", "text-gray-900");
				btn.classList.add("text-gray-600");
			});

			// 클릭된 버튼에 활성화 스타일 적용
			this.classList.add("bg-gray-300", "text-gray-900");
			this.classList.remove("text-gray-600");

			// pageManager를 통한 페이지 전환
			pageManager.switchPage(pageId.replace("dashboard-", ""));
			pageManager.updateButtonStyles(this);
		});
	});

	// 초기 대시보드 버튼 스타일 설정
	const firstDashboardButton = document.querySelector(
		'[data-page="dashboard-one"]'
	);
	if (firstDashboardButton) {
		firstDashboardButton.classList.add("bg-gray-300", "text-gray-900");
		firstDashboardButton.classList.remove("text-gray-600");
	}
});

function showChart(chartId) {
	const charts = document.querySelectorAll(".chart-container");
	const selectedChart = document.getElementById(chartId);

	// DOM 조작 최소화
	requestAnimationFrame(() => {
		charts.forEach((chart) => {
			chart.style.display = "none";
		});
		if (selectedChart) {
			selectedChart.style.display = "block";

			// 차트 리사이즈는 디바운스 처리
			if (window.chartResizeTimeout) {
				clearTimeout(window.chartResizeTimeout);
			}
			window.chartResizeTimeout = setTimeout(() => {
				window.dispatchEvent(new Event("resize"));
			}, 100);
		}
	});
}

// 페이지 매니저 객체 정의
const pageManager = {
	switchPage(pageId) {
		// 모든 콘텐츠 숨기기/보이기를 requestAnimationFrame으로 최적화
		requestAnimationFrame(() => {
			document
				.querySelectorAll('[id^="dashboard-content-"]')
				.forEach((content) => {
					content.classList.add("hidden");
				});
			const selectedContent = document.getElementById(
				`dashboard-content-${pageId}`
			);
			if (selectedContent) {
				selectedContent.classList.remove("hidden");
				// 차트 리사이즈 디바운싱
				this.triggerChartResize();
			}
			// 헤더 타이틀 업데이트
			const headerTitles = {
				one: {
					title: "첫번째",
					subtitle: "카드 사용 현황 및 분석 리포트",
				},
				two: {
					title: "두번째",
					subtitle: "회원 이용 패턴 및 분석",
				},
				three: {
					title: "세번째",
					subtitle: "워드 클라우드 및 감성 분석",
				},
			};
			header = document.getElementById("dashboard-header");
			header.querySelector("h1").textContent = headerTitles[pageId].title;
			header.querySelector("p").textContent = headerTitles[pageId].subtitle;
		});
	},

	updateButtonStyles(activeButton) {
		// 버튼 스타일 업데이트를 requestAnimationFrame으로 최적화
		requestAnimationFrame(() => {
			document.querySelectorAll(".sidebar-button").forEach((btn) => {
				btn.classList.remove("bg-gray-300");
			});
			activeButton.classList.add("bg-gray-300");
		});
	},

	// 차트 리사이즈 디바운스 함수
	triggerChartResize: (() => {
		let resizeTimeout;
		return () => {
			if (resizeTimeout) clearTimeout(resizeTimeout);
			resizeTimeout = setTimeout(() => {
				window.dispatchEvent(new Event("resize"));
			}, 100);
		};
	})(),
};

// 채팅봇 객체 정의
const chatbot = {
	toggleWindow() {
		const chatWindow = document.getElementById("chat-window");
		chatWindow.classList.toggle("hidden");
	},

	closeWindow() {
		document.getElementById("chat-window").classList.add("hidden");
	},

	appendMessage(message, isUser) {
		const messagesContainer = document.getElementById("chat-messages");
		const messageElement = this.createMessageElement(message, isUser);

		// DOM 조작 최적화
		requestAnimationFrame(() => {
			messagesContainer.appendChild(messageElement);
			messagesContainer.scrollTop = messagesContainer.scrollHeight;
		});
	},

	createMessageElement(message, isUser) {
		const div = document.createElement("div");
		div.className = `flex ${isUser ? "justify-end" : "justify-start"} mb-4`;
		div.innerHTML = `
			<div class="max-w-[70%] ${
				isUser ? "bg-blue-500 text-white" : "bg-gray-200"
			} rounded-lg px-4 py-2">
				<p class="text-sm">${message}</p>
			</div>
		`;
		return div;
	},

	async sendMessage(message) {
		try {
			const response = await fetch("/chatbot/message/", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					"X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
						.value,
				},
				body: JSON.stringify({ message }),
			});

			if (!response.ok) throw new Error("Network response was not ok");

			const data = await response.json();
			this.appendMessage(data.response, false);
		} catch (error) {
			console.error("Error:", error);
			this.appendMessage("죄송합니다. 오류가 발생했습니다.", false);
		}
	},
};

// 차트 설정 초기화 함수
function initializeChartConfigs(chartData) {
	Object.entries(chartData).forEach(([chartId, data]) => {
		if (!data.layout) {
			data.layout = {};
		}

		// 기본 레이아웃 설정
		data.layout = {
			...data.layout,
			autosize: true,
			margin: { t: 0, l: 0, r: 0, b: 0 },
			paper_bgcolor: "rgba(0,0,0,0)",
			plot_bgcolor: "rgba(0,0,0,0)",
			font: {
				family: "Roboto, sans-serif",
			},
		};

		// 인디케이터 차트에 대한 처리
		if (chartId.includes("indicator")) {
			data.layout.responsive = true;
		}
	});

	return chartData;
}
