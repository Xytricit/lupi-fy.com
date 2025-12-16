class InputSystem {
  touchPoints = new Map<number, { x: number; y: number; timestamp: number }>();
  gestureState = {
    pinch: { active: false, distance: 0, startDistance: 0 },
    swipe: { active: false, direction: '', startTime: 0 },
    tap: { count: 0, lastTapTime: 0 }
  };
  touchThreshold = 30;
  doubleTapInterval = 300;
  pinchThreshold = 0.2;

  constructor() {
    this.initEventListeners();
  }

  initEventListeners() {
    window.addEventListener('touchstart', this.handleTouchStart.bind(this));
    window.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
    window.addEventListener('touchend', this.handleTouchEnd.bind(this));
    window.addEventListener('touchcancel', this.handleTouchCancel.bind(this));
  }

  handleTouchStart(e: TouchEvent) {
    e.preventDefault();
    const now = Date.now();
    
    for (let i = 0; i < e.touches.length; i++) {
      const touch = e.touches[i];
      this.touchPoints.set(touch.identifier, {
        x: touch.clientX,
        y: touch.clientY,
        timestamp: now
      });
    }

    if (e.touches.length === 1) {
      if (now - this.gestureState.tap.lastTapTime < this.doubleTapInterval) {
        this.gestureState.tap.count++;
        this.dispatchGestureEvent('doubletap', {
          x: e.touches[0].clientX,
          y: e.touches[0].clientY
        });
      } else {
        this.gestureState.tap.count = 1;
      }
      this.gestureState.tap.lastTapTime = now;
    } else if (e.touches.length === 2) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = this.getDistance(
        touch1.clientX, touch1.clientY,
        touch2.clientX, touch2.clientY
      );
      this.gestureState.pinch = {
        active: true,
        distance: distance,
        startDistance: distance
      };
      this.dispatchGestureEvent('pinchstart', {
        distance: distance,
        center: this.getMidpoint(touch1, touch2)
      });
    }
  }

  handleTouchMove(e: TouchEvent) {
    e.preventDefault();
    
    for (let i = 0; i < e.touches.length; i++) {
      const touch = e.touches[i];
      const touchPoint = this.touchPoints.get(touch.identifier);
      if (touchPoint) {
        touchPoint.x = touch.clientX;
        touchPoint.y = touch.clientY;
      }
    }

    if (e.touches.length === 1 && !this.gestureState.swipe.active) {
      const touch = e.touches[0];
      const startTouch = Array.from(this.touchPoints.values())[0];
      const dx = touch.clientX - startTouch.x;
      const dy = touch.clientY - startTouch.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      
      if (dist > this.touchThreshold) {
        const now = Date.now();
        this.gestureState.swipe = {
          active: true,
          direction: Math.abs(dx) > Math.abs(dy) 
            ? (dx > 0 ? 'right' : 'left') 
            : (dy > 0 ? 'down' : 'up'),
          startTime: now
        };
        this.dispatchGestureEvent('swipe', {
          direction: this.gestureState.swipe.direction,
          velocity: dist / (now - startTouch.timestamp)
        });
      }
    }

    if (e.touches.length === 2 && this.gestureState.pinch.active) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const currentDistance = this.getDistance(
        touch1.clientX, touch1.clientY,
        touch2.clientX, touch2.clientY
      );
      const scale = currentDistance / this.gestureState.pinch.startDistance;
      
      if (Math.abs(scale - 1) > this.pinchThreshold) {
        this.dispatchGestureEvent('pinch', {
          scale: scale,
          center: this.getMidpoint(touch1, touch2)
        });
      }
    }
  }

  handleTouchEnd(e: TouchEvent) {
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      this.touchPoints.delete(touch.identifier);
    }

    if (e.touches.length === 0) {
      if (!this.gestureState.swipe.active && this.gestureState.tap.count === 1) {
        const touch = e.changedTouches[0];
        this.dispatchGestureEvent('tap', {
          x: touch.clientX,
          y: touch.clientY,
          count: 1
        });
      }
      
      this.gestureState.swipe = { active: false, direction: '', startTime: 0 };
      this.gestureState.pinch = { active: false, distance: 0, startDistance: 0 };
    } else if (e.touches.length === 1 && this.gestureState.pinch.active) {
      this.dispatchGestureEvent('pinchend', {});
      this.gestureState.pinch.active = false;
    } else if (e.touches.length === 1) {
      this.dispatchGestureEvent('pinchend', {});
    }
  }

  handleTouchCancel(e: TouchEvent) {
    this.touchPoints.clear();
    this.gestureState = {
      pinch: { active: false, distance: 0, startDistance: 0 },
      swipe: { active: false, direction: '', startTime: 0 },
      tap: { count: 0, lastTapTime: 0 }
    };
  }

  getDistance(x1: number, y1: number, x2: number, y2: number): number {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  }

  getMidpoint(touch1: Touch, touch2: Touch) {
    return {
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    };
  }

  dispatchGestureEvent(type: string, data: any) {
    const event = new CustomEvent(`gesture:${type}`, { detail: data });
    window.dispatchEvent(event);
  }

  getTouchPositions() {
    return Array.from(this.touchPoints.values()).map(point => ({
      x: point.x,
      y: point.y
    }));
  }

  isTouchActive() {
    return this.touchPoints.size > 0;
  }

  getGestureState() {
    return this.gestureState;
  }
}

function onGesture(type: string, callback: (data: any) => void) {
  window.addEventListener(`gesture:${type}`, (e: any) => {
    callback(e.detail);
  });
}

export function getTouchCount() {
  return inputSystem.touchPoints.size;
}

export function getTouchPosition(index = 0) {
  const positions = inputSystem.getTouchPositions();
  return positions[index] || { x: 0, y: 0 };
}

export function onTouchStart(callback: (touch: { x: number; y: number; id: number }) => void) {
  window.addEventListener('touchstart', (e: TouchEvent) => {
    e.preventDefault();
    for (let i = 0; i < e.changedTouches.length; i++) {
      const touch = e.changedTouches[i];
      callback({
        x: touch.clientX,
        y: touch.clientY,
        id: touch.identifier
      });
    }
  }, { passive: false });
}

export function onSwipe(callback: (direction: string, velocity: number) => void) {
  onGesture('swipe', (data) => {
    callback(data.direction, data.velocity);
  });
}

export function onPinch(callback: (scale: number, center: { x: number; y: number }) => void) {
  let isPinching = false;
  let startScale = 1;
  
  onGesture('pinchstart', (data) => {
    isPinching = true;
    startScale = 1;
  });
  
  onGesture('pinch', (data) => {
    if (isPinching) {
      callback(data.scale, data.center);
    }
  });
  
  onGesture('pinchend', () => {
    isPinching = false;
  });
}

export function onDoubleTap(callback: (position: { x: number; y: number }) => void) {
  onGesture('doubletap', (data) => {
    callback({ x: data.x, y: data.y });
  });
}

const inputSystem = new InputSystem();
export default inputSystem;
